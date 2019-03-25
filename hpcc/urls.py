"""hpcc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from login.views import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from login import views as loginview

urlpatterns = [
    path('', home, name='name'),
    path('ScriptGen/', include('ScriptGen.urls')),
    path('jobs/', include('job_view.urls')),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', auth_views.LoginView, name='auth'),
    url(r'^home/$', views.index, name='home'),
    url(r'^register/$', register, name='register'),
    url(r'^register/success/$', register_success, name='register_success'),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^auth/msunet/callback', loginview.msunet_callback, name='msunet_callback'),
    url(r'^logout/$', logout_page, name='logout'),
    path('stats/', include('stats.urls')),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

