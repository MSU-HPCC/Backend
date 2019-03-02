from django.urls import path

from . import views

urlpatterns = [
    path('', views.JobSubStats, name='index'),
    path('jobStats/', views.JobSubStats,name='JobStats'),
    path('FailStats/', views.JobFailure,name='FailStats'),
    path('MajorUsers/', views.MajorUsers,name='MajorUsers'),
    path('1d/', views.Graph.as_view(), name='plot1d'),
]