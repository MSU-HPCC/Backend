from django.urls import path

from . import views

urlpatterns = [

    path('', views.jobs, name='jobs'),
    path('group/', views.groupJobs, name='index'),
    path('<str:user>/', views.adminJobs, name='index'),
]
