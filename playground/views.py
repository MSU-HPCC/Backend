import os
import io
import pyslurm
import shutil
import ntpath
import time
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
            # handle uploaded files
            uploaded_bash_script = request.FILES['bash']
            uploaded_source_code = request.FILES['source']
            fs = FileSystemStorage()
            bash_name = fs.save(uploaded_bash_script.name, uploaded_bash_script)
            source_name = fs.save(uploaded_source_code.name, uploaded_source_code)
            print("bash: {}, source: {}".format(bash_name, source_name))

            # is at /web/Backend or /var/www/html
            bash_name_components = bash_name.split('_')  ## TODO Bash.sb turned to Bash.sb.sb -- idk why
            clean_bash_str = bash_name_components[0] + '.sb'
            source_name_components = source_name.split('_') ## TODO CANNOT USE THIS FOR FILES WITH _ in them...............
            clean_source_str = source_name_components[0] + '.py' ## TODO adding proper file extension handling for .cpp ect.
            os.system("docker container stop slurm-container")
            os.system("docker container rm slurm-container")
            os.system("mkdir -p /playground_uploads")
            os.system("mv uploads/{} /playground_uploads/{}".format(bash_name, clean_bash_str))
            os.system("mv uploads/{} /playground_uploads/{}".format(source_name, clean_source_str))
            #os.system("cd /playground_uploads;sbatch {}".format(clean_bash_str))

            # launch playground
            os.system("docker run --name slurm-container -v /playground_uploads:/playground --net=host -it -h ernie slurm-dev-pg")  # job files are placed into container at /playground
            time.sleep(90) # sleep for 90 seconds to make sure container is running...
            os.system("docker exec -it slurm-container '/usr/bin/python3 ./playground_monitor.py'") #  run the playground.py script in container
            print("this is after running monitor")
            print("going to sleep now...")
            time.sleep(8 * 60)
            print(os.popen("ls /playground_uploads").read())

            confMessage = ''
            f = open('playground_result.txt')
            for line in f:
                confMessage += line
                print("output lines: {}".format(line))



            return render(request, 'playground/confirmation.html', {'user': request.user, 'bash' : bash_name, 'source' : source_name, 'message' : confMessage, })
    return render(request, 'playground/confirmation.html', {'user': request.user, })

def result(request):
    testvar = 'thetest'
    return render(request, 'playground/result.html', {'user': request.user,})
