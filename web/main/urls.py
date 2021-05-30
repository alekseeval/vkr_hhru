from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('accounts.urls')),

    path('', views.home, name='home'),
    path('app/', views.home),
    path('app/resume/list', views.resume_list, name='resume_list'),
    path('app/resume', views.resume, name='resume'),
]
