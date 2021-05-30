from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login, logout
import requests

from .models import HhUser
from django.contrib.auth.models import User

from typing import Final

import sys
sys.path.append('..')
from data_parsers.hhApiParser import HhApiParser

REDIRECT_URI: Final = 'http://127.0.0.1:8000/auth'
CLIENT_ID: Final = 'N2AFEUCFSBS581GFMQBM7QAG90C05O1H54KP8KCACNOOU8V21SS6O8DPAA6KVDCL'
CLIENT_SECRET: Final = 'I9VAE4I4POC61MFU31J9S55FBBGC345VAFSBN611RDVUA8BN1J3JH9U3D2M0V8PN'


def login_view(request):
    if request.method == 'GET':
        logout(request)
        return render(request, 'accounts/login.html')
    elif request.method == 'POST':
        return redirect(f'https://hh.ru/oauth/authorize?' +
                        f'response_type=code' +
                        f'&client_id={CLIENT_ID}' +
                        f'&redirect_uri={REDIRECT_URI}')


def login_catch_user_code(request):
    user_code = request.GET.get("code", None)
    if user_code is None:
        return redirect('login', {'error': 'Отказано в доступе'})
    req_args = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': user_code,
    }
    response = requests.post('https://hh.ru/oauth/token', req_args)
    token_data = response.json()

    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    parser = HhApiParser()
    account_data = parser.get_auth_info(access_token)

    if not HhUser.objects.filter(hh_id=account_data.get('id')):
        user = User(first_name=account_data.get('first_name'), last_name=account_data.get('last_name'), email=account_data.get('email'))
        user.save()
        hh_user = HhUser(middle_name=account_data.get('middle_name'), hh_id=account_data.get('id'),
                         access_token=access_token, refresh_token=refresh_token,
                         user=user)
        hh_user.save()
    else:
        hh_user = HhUser.objects.get(hh_id=account_data.get('id'))
        hh_user.access_token = access_token
        hh_user.refresh_token = refresh_token
        hh_user.save()
        user = User.objects.get(id=hh_user.user.id)
    login(request, user)
    request.session.set_expiry(token_data.get('expires_in') - 30)
    print(f'---> Session expires in {token_data.get("expires_in") - 30}')

    return redirect('home')


def logout_view(request):
    logout(request)
    return redirect('login')
