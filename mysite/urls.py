from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from login.views import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', auth_views.login, name='auth'),
    url(r'^home/$', home, name='home'),
    url(r'^register/$', register, name='register'),
    url(r'^register/success/$', register_success, name='register_success'),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^logout/$', logout_page, name='logout'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)