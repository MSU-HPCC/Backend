from django.urls import path

from . import views

urlpatterns = [
    path('', views.AvgWait, name='index'),
    path('jobStats/', views.JobSubStats,name='JobStats'),
    path('FailStats/', views.JobFailure,name='FailStats'),
    path('MajorUsers/', views.MajorUsers,name='MajorUsers'),
    path('AvgWait/',views.AvgWait,name='AvgWait')

]