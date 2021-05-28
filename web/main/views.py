from django.shortcuts import render


def home(request):
    return render(request, 'main/home.html', {'active_el': 'home'})


def resume_list(request):
    # TODO: Написать функционал по получению резюме пользователя
    resumes = [
        'resume1',
        'resume2',
        'resume3',
        'resume4',
        'resume5'
    ]
    return render(request, 'main/resume_list.html', {'active_el': 'rl_list', 'resumes': resumes})
