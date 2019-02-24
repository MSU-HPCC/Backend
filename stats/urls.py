from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('jobStats/', views.JobSubStats,name='JobStats'),
    path('FailStats/', views.JobFailure,name='FailStats')
]