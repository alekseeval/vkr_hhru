from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('resume/list', views.resume_list, name='resume_list'),
    path('resume', views.resume, name='resume'),
    path('login', views.login, name='login'),
]
