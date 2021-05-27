from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('resume/list', views.resume_list, name='resume_list')
]
