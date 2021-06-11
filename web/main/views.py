from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
import operator

import sys
sys.path.append('..')
from accounts.models import HhUser
from data_parsers.hhApiParser import HhApiParser
from services.db_service import DbService
from workflow import recommendations


MONTH_LIST = ['январь', 'февраль', 'март', 'апрел', 'май', 'июнь',
           'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']


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
    parser = HhApiParser()
    access_token = HhUser.objects.get(user_id=request.user.id).access_token

    username = get_user_name(request)
    resume_id = request.GET.get("resume_id", "")
    top_resumes = get_top_resumes(request)

    info = parser.get_applicant_resume_data(resume_id, access_token)

    db_service = DbService()
    currencies_db = db_service.execute_script('select code from currency')
    currencies = [cur[0] for cur in currencies_db]

    # Получить рекомендации по резюме
    warnings = get_recommendations(info, request)
    warnings.sort(key=operator.itemgetter('type'))

    # Обработать дату
    for exp in info['experience']:
        start = datetime.datetime.fromisoformat(exp['start'])
        exp['start'] = start.strftime(f'{MONTH_LIST[start.month-1]} %Y')

        if exp['end'] is not None:
            end = datetime.datetime.fromisoformat(exp['end'])
            exp['end'] = end.strftime(f'{MONTH_LIST[end.month - 1]} %Y')

    return render(request, 'main/resume_edit.html', {'active_el': resume_id,
                                                     'user': username,
                                                     'resume': info,
                                                     'warnings': warnings,
                                                     'top_resumes': top_resumes,
                                                     'currencies': currencies,
                                                     })


@login_required
def resume_save(request):

    resume_id = request.GET.get('id', '')

    change_params = {
        'last_name': request.GET.get('last_name', ''),
        'first_name': request.GET.get('first_name', ''),
        'title': request.GET.get('title', ''),
        'birth_date': request.GET.get('birth_date', ''),
    }
    salary_amount = request.GET.get('salary_amount', 0)
    salary_currency = request.GET.get('salary_currency', 'RUR')
    middle_name = request.GET.get('middle_name', '')
    skills = request.GET.get('skills', '')

    if salary_amount != "":
        if salary_currency != 'Валюта':
            change_params['salary'] = {'amount': salary_amount, 'currency': salary_currency}
        else:
            change_params['salary'] = {'amount': salary_amount, 'currency': 'RUR'}
    else:
        change_params['salary'] = {'amount': 0, 'currency': 'RUR'}

    if middle_name == '':
        middle_name = None
    change_params['middle_name'] = middle_name
    if skills == '':
        skills = None
    change_params['skills'] = skills

    parser = HhApiParser()
    access_token = HhUser.objects.get(user_id=request.user.id).access_token
    parser.change_user_resume_data(resume_id, change_params, access_token)

    return redirect(f'http://127.0.0.1:8000/app/resume?resume_id={resume_id}')


# ----------------------------------------------------------------------------------------------------------------------
def get_top_resumes(request):
    parser = HhApiParser()
    resumes = parser.get_applicant_resumes(HhUser.objects.get(user_id=request.user.id).access_token)
    top_resumes = [r for r in resumes['items'] if r['status']['id'] == 'published']
    return top_resumes[:3]


def get_all_resumes(request):
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


def get_recommendations(resume_info, request):

    access_token = HhUser.objects.get(user_id=request.user.id).access_token
    warnings = []

    # Проверка фотографии
    rec = recommendations.check_photo(resume_info['photo'])
    if rec:
        warnings.append(rec)

    # Подсказки для заголовка резюме
    rec = recommendations.get_vacancy_title_recommendation(resume_info['title'])
    if rec:
        warnings.append(rec)

    # Проверка ЗП
    rec = recommendations.check_salary(resume_info['salary'], resume_info['id'], access_token)
    if rec:
        warnings.append(rec)

    # Проверка опыта работы
    rec = recommendations.check_experience(resume_info['experience'])
    if rec:
        warnings.append(rec)

    # Проверка наличия рекомендаций с прошлого места работы
    if len(resume_info['experience']) != 0:
        rec = recommendations.check_work_recommendations(resume_info['recommendation'])
        if rec:
            warnings.append(rec)

    # Проверка ключевых навыков
    rec = recommendations.check_key_skills(resume_info['skill_set'])
    if rec:
        warnings.append(rec)

    # Проверка поля "Обо мне"
    rec = recommendations.check_skills(resume_info['skills'])
    if rec:
        warnings.append(rec)

    return warnings
