import os
import io
import pyslurm
import shutil
import ntpath
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from pathlib import Path
# Create your views here.
def setup(request):
    if request.method == 'POST':
        print("is post")
        if request.FILES:
            return confirmation(request)
    else:
        return render(request, 'playground/setup.html', {'user': request.user,})

def confirmation(request):
    if request.method == 'POST':
        print("in post")
        if request.FILES:
            print("found files")
            uploaded_bash_script = request.FILES['bash']
            uploaded_source_code = request.FILES['source']
            fs = FileSystemStorage()
            bash_name = fs.save(uploaded_bash_script.name, uploaded_bash_script)
            source_name = fs.save(uploaded_source_code.name, uploaded_source_code)
            print("bash: {}, source: {}".format(bash_name, source_name))
            teststr = "THIS IS MY DUMP STRING"
            os.system("echo 'wow this is post confirmation screen 0.0' >> testossystemfile")
            return render(request, 'playground/confirmation.html', {'user': request.user, 'bash' : bash_name, 'source' : source_name, 'teststr' : teststr, })
    return render(request, 'playground/confirmation.html', {'user': request.user, })

def result(request):
    testvar = 'thetest'
    return render(request, 'playground/result.html', {'user': request.user,})
