from django.shortcuts import render


def home(request):
    top_resumes = get_top_resumes()
    return render(request, 'main/home.html', {'active_el': 'home',
                                              'top_resumes': top_resumes,
                                              })


def resume_list(request):
    resumes = get_all_resumes()
    top_resumes = get_top_resumes()

    return render(request, 'main/resume_list.html', {'active_el': 'rl_list',
                                                     'resumes': resumes,
                                                     'top_resumes': top_resumes,
                                                     })


def resume(request):

    resume_id = request.GET.get("resume_id", "")
    top_resumes = get_top_resumes()

    # TODO: Получить информацию о конкретном резюме пользователя
    info = {
        'id': resume_id,
        'title': 'Мое резюме',
        'desc': 'Это тестовый вывод информации по резюме'
    }

    return render(request, 'main/resume_edit.html', {'active_el': resume_id,
                                                     'resume_info': info,
                                                     'top_resumes': top_resumes,
                                                     })


# ----------------------------------------------------------------------------------------------------------------------
# TODO: Написать функционал по получению первых 5 резюме пользователя
def get_top_resumes():
    return [
        {'title': 'resume1', 'id': '1'},
        {'title': 'resume2', 'id': '2'},
        {'title': 'resume3', 'id': '3'},
        {'title': 'resume4', 'id': '4'},
        {'title': 'resume5', 'id': '5'}
    ]


# TODO: Написать функционал по получению всех резюме пользователя
def get_all_resumes():
    return [
        {'title': 'resume1', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '1'},
        {'title': 'resume2', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '2'},
        {'title': 'resume3', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '3'},
        {'title': 'resume4', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '4'},
        {'title': 'resume5', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '5'},
        {'title': 'resume6', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '6'},
        {'title': 'resume7', 'desc': 'Краткое описание резюме, в которое, пока не известно что вставить', 'id': '7'}
    ]
