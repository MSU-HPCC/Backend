from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('bash/', views.get_name, name='get_name'),
    path('create_form/', views.ScriptGen_create_view, name='create_form'),
    path('SubmitJob/', views.SubmitJob, name= "SubmitJob"),
    path('download/', views.downloadFile, name ="download"),
    path('Update/', views.Update, name="Update"),
    path('jobqueue/',views.CleanUp,name="CleanUp"),
    path('Results/',views.Results, name="Results"),
    path('SlurmFile/', views.SlurmFile,name="Results"),
    path('Test/',views.Test, name="Test")

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
