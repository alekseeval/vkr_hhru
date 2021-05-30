from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required

import sys
sys.path.append('..')
from accounts.models import HhUser
from data_parsers.hhApiParser import HhApiParser


@login_required
def home(request):
    top_resumes = get_top_resumes(request)
    username = get_user_name(request)
    return render(request, 'main/home.html', {'active_el': 'home',
                                              'top_resumes': top_resumes,
                                              'user': username,
                                              })


@login_required
def resume_list(request):
    username = get_user_name(request)
    resumes = get_all_resumes(request)
    top_resumes = resumes[:5]

    return render(request, 'main/resume_list.html', {'active_el': 'rl_list',
                                                     'user': username,
                                                     'resumes': resumes,
                                                     'top_resumes': top_resumes,
                                                     })


@login_required
def resume(request):
    username = get_user_name(request)
    resume_id = request.GET.get("resume_id", "")
    top_resumes = get_top_resumes(request)

    # TODO: Получить информацию о конкретном резюме пользователя
    info = {
        'id': resume_id,
        'title': 'Мое резюме',
        'desc': 'Это тестовый вывод информации по резюме'
    }

    return render(request, 'main/resume_edit.html', {'active_el': resume_id,
                                                     'user': username,
                                                     'resume_info': info,
                                                     'top_resumes': top_resumes,
                                                     })


# ----------------------------------------------------------------------------------------------------------------------
# TODO: Написать функционал по получению первых 5 резюме пользователя
def get_top_resumes(request):
    if not HhUser.objects.filter(user_id=request.user.id):
        return [
            {'title': 'resume1', 'id': '1'},
            {'title': 'resume2', 'id': '2'},
            {'title': 'resume3', 'id': '3'},
            {'title': 'resume4', 'id': '4'},
            {'title': 'resume5', 'id': '5'}
        ]

    parser = HhApiParser()
    resumes = parser.get_applicant_resumes(HhUser.objects.get(user_id=request.user.id).access_token)
    top_resumes = [r for r in resumes['items'] if r['status']['id'] == 'published']
    return top_resumes[:5]


# TODO: Написать функционал по получению всех резюме пользователя
def get_all_resumes(request):
    if not HhUser.objects.filter(user_id=request.user.id):
        return [
            {'title': 'resume1', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '1'},
            {'title': 'resume2', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '2'},
            {'title': 'resume3', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '3'},
            {'title': 'resume4', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '4'},
            {'title': 'resume5', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '5'},
            {'title': 'resume6', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '6'},
            {'title': 'resume7', 'skills': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '7'}
        ]
    parser = HhApiParser()
    resumes = parser.get_applicant_resumes(HhUser.objects.get(user_id=request.user.id).access_token)['items']
    access_token = HhUser.objects.get(user_id=request.user.id).access_token

    resumes_full_info = [parser.get_applicant_resume_data(item['id'], access_token) for item in resumes if item['status']['id'] == 'published']

    return resumes_full_info

def get_user_name(request):
    user = request.user
    if HhUser.objects.filter(user_id=user.id):
        hh_user = HhUser.objects.get(user_id=user.id)
        return str(hh_user)
    else:
        return user.username
