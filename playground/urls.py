from django.urls import path

from . import views

urlpatterns = [

    path('', views.setup, name='setup'),
    path('confirmation/', views.confirmation, name='playground-confirmation'),
    path('result/', views.result, name='playground-result'),
]
