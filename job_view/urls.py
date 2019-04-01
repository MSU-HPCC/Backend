from django.urls import path

from . import views

urlpatterns = [

    path('', views.jobs, name='jobs'),
    path('group/', views.groupJobs, name='index'),
    path('admin/', views.adminJobs, name='index'),
    path('<str:user>/', views.adminSearch, name='index'),
]
