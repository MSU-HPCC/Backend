from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:user>/jobs/', views.jobs, name='jobs'),
    path('get_name/', views.get_name, name='get_name'),
    path('create_form/', views.ScriptGen_create_view, name='create_form')
]
