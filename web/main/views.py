from django.shortcuts import render


def home(request):
    return render(request, 'main/home.html', {'active_el': 'home'})


def resume_list(request):
    return render(request, 'main/resume_list.html', {'active_el': 'rl_list'})
