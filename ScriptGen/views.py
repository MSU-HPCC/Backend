from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse
import os
import io

from . import hpcccreds

import paramiko

import os
import time
from django.views.decorators.csrf import csrf_exempt

from django.core.files.storage import FileSystemStorage
def index(request):
    return HttpResponse("We are at the script generation page")

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NameForm
from .models import ScriptGenInfo
from django.http import JsonResponse
import pyslurm
import shutil
import ntpath
from pathlib import Path
from datetime import datetime
def ScriptGen_create_view(request):
    '''
    form = NameForm(request.POST or None)
    if form.is_valid():
        form.save()
    context={
        'form':form
    }
    return render(request,'ScriptGen/form_create.html',context)'''
    filename = os.getcwd()+ "/ScriptGen/Bash.sb"
    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' + 'Bash.sb'

    response['Content-Length'] = os.path.getsize(filename)

    # return response


    return response

    '''
    wrapper = FileWrapper(open((filename),"r"))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response'''

def SlurmFile(request):
    jobid = request.GET.get('dir','')
    filename = os.getcwd() + "/JobSub/"+str(jobid)+"/slurm-"+str(jobid)+".out"
    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' +"slurm-"+str(jobid)+".out"

    response['Content-Length'] = os.path.getsize(filename)

    # return response

    return response
    return HttpResponse("ok")

def downloadFile(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        print(uploaded_file.name)
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'ScriptGen/download.html', context)
@csrf_exempt
def get_name(request):




    SubmittedJob = False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = NameForm(request.POST)
        #if request.POST.get('action') == "Update Bash Script":
        '''
        if request.is_ajax():
            print("here")
            text = request.POST.get('text', 1)
            print(text)
            FilePreview = text.split("\n")
            dictionary = request.GET
            dict2 = request.POST
            user = request.GET.get('username', 1)
            filename = os.getcwd() + "\ScriptGen\Bash.qsub"
            file = open(filename, "w")
            file.write(text)
            file.close()
            print("end")
            response = Update(request,text)
            return response
            return render(request, 'ScriptGen/download.html')

        '''

        form = NameForm(request.POST)
        # file upload
        if request.FILES:
            #script_path = form.cleaned_data['CodeDirectory']
            uploaded_file = request.FILES['document']

            fs = FileSystemStorage()
            name = fs.save(uploaded_file.name, uploaded_file)
            filename = uploaded_file.name
            bashFile = uploaded_file.name.split(".")[0] + '.sb'
            #bashpath = os.getcwd() + r'\ScriptGen" + bashFile
            bashpath =os.path.join(os.getcwd()+"/ScriptGen", "Bash.sb")
            script = fs.path(name)
            # submit a job
            user = request.user.username
            Success = SubmitJob(bashpath, script, filename,user)
            if Success==True:

                return render(request, 'ScriptGen/success.html',{'message':"Job Successfully Scheduled!"})
            else:
                return render(request, 'ScriptGen/success.html', {'message': "Job Unsuccessfully Scheduled"})



        # create a form instance and populate it with data from the request:

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:

            CPUs = form.cleaned_data['CPUs']
            Wall_time = form.cleaned_data['Wall_time']
            job_name = form.cleaned_data['job_name']
            #script_path = form.cleaned_data['CodeDirectory']
            nodes = form.cleaned_data['nodes']
            #memory = form.cleaned_data['memory']
            MemoryPerCPu = form.cleaned_data['MemoryPerCPU']
            Tasks = form.cleaned_data['Tasks']
            Executable = form.cleaned_data['ExecutableName']
            #filename = os.getcwd() + r"\ScriptGen\\"+ Executable.split(".")[0]+".qsub"
            filename = os.getcwd() + r"/ScriptGen/Bash.sb"
            file = io.open(filename, "w", newline='\n')
            os.chmod(filename,0o664)





            file.write("#!/bin/bash \n\n")
            file.write('##SBATCH Lines for Resource Request ##\n\n')

            file.write("#SBATCH --time=" + str(Wall_time) + "\n")
            file.write("#SBATCH --nodes=" + str(nodes) + "\n")
            file.write("#SBATCH --tasks=" + str(Tasks) + "\n")
            file.write("#SBATCH --mem-per-cpu=" + str(MemoryPerCPu) + "\n")
            file.write("#SBATCH -J " + str(job_name) + "\n")
            file.write("##Command Lines to Run ## \n\n")
            #file.write("cd "+str(script_path)+"\n")
            #file.write("srun -n "+str(Tasks)+" "+str(Executable)+"\n")

            #add compilation and execution logic
            if Executable.endswith(".py"):

                file.write("srun -n "+str(Tasks)+" " +"python ./"+str(Executable)+"\n")
            if Executable.endswith(".c"):
                file.write("gcc "+Executable+" -o "+Executable[0:len(Executable)-2] +"\n")
                file.write("srun -n "+str(Tasks)+" "+"./"+str(Executable[0:len(Executable)-2]))
            if Executable.endswith(".cpp"):
                file.write("g++ "+Executable+" -o "+Executable[0:len(Executable)-4] +"\n")
                file.write("srun -n "+str(Tasks)+" "+"./"+str(Executable[0:len(Executable)-4]))



            ########
            file.close()
            file = open(filename,"rb")
            response = HttpResponse(file.read())
            file.close()
            # get list of lines to return to template
            file = open(filename,"r")
            FilePreview = []
            for line in file:
                FilePreview.append(line)
            file.close()

            #########





            return render(request, 'ScriptGen/preview.html', {'preview': FilePreview, 'form': form, 'filePath': filename})


    # if a GET (or any other method) we'll create a blank form
    else:
        data = {'Wall_time':'HH:MM:SS','job_name':'job name','nodes':'1','CPUs':'1','MemoryPerCPU':'1M or 1G','Tasks':'1','ExecutableName':'example.py'}
        form = NameForm(initial=data)

    return render(request, 'ScriptGen/name.html', {'form': form})


def SubmitJob(bashpath, script, filename,user):
    print("bash = "+bashpath)
    print("script = "+script)
    print("filename = "+filename)
    currDir = os.getcwd()
    #go into jobsub folder to execute batch script
    os.chdir("JobSub")
    # copy bashfile and script into JobSub directory
    shutil.copy(script, os.getcwd())
    shutil.copy(bashpath, os.getcwd())
    # grab the Bash Scriptname and Script name form the full paths
    BashScriptName = ntpath.basename(bashpath)
    ScriptName = ntpath.basename(script)
    # rename the script to what is listed in the bash file
    os.rename(ScriptName,filename)
    # submit a job
    a=pyslurm.job()
    print("files = "+str(os.listdir(os.getcwd())))
    # get the jobid so we know what folder to put the files in


    try:
        jobid = a.submit_batch_job({'script': BashScriptName})
        print("we are trying")

    except Exception:
        os.chdir("..")

        return False

    print("jobid = "+str(jobid))
    # make the directory with full permisions
    # it will be named after the jobid
    os.mkdir(str(jobid), mode=0o777)
    # move the bash script, actual script, and slurm.out to new folder jobid
    # if jobid=13, the folder is named 13
    #shutil .move(BashScriptName, str(jobid))
    #shutil.move(filename, str(jobid))
    slurmname= "slurm-"+str(jobid)+".out"
    print(slurmname)
    print(os.getcwd())

    if os.path.isfile(slurmname):
        print("slurm file exists")
        shutil.move(slurmname, str(jobid))
    shutil.move(BashScriptName, str(jobid))
    time.sleep(0.3)
    shutil.copy(filename, str(jobid))

    #shutil.move(filename, str(jobid))
    # go back to original directory not to fuck with anything
    os.chdir("..")





    os.chdir("/home/"+user)
    os.mkdir("testing", mode=0o777)
    os.chdir(currDir)

    return True


@csrf_exempt
def Update(request):
    print("we are updating")
    text = request.GET.get('text',1)
    FilePreview = text.split("\n")
    #FilePreview=[]
    dictionary = request.GET
    dict2 = request.POST
    #user = request.GET.get('username',1)
    filename = os.getcwd() + "/ScriptGen/Bash.sb"
    #file = open(filename, "w")
    file = io.open(filename, "w", newline='\n')
    file.write(text)
    file.close()
    form = NameForm()
    #return render(request, 'ScriptGen/preview.html', {'preview': FilePreview, 'form': form, 'filePath': filename})
    return render(request,'ScriptGen/download.html')


def CleanUp(request):
    for file in os.listdir("JobSub"):
        if file.endswith(".out"):
            jobID= file.split(".")[0]
            jobID= jobID.split("-")[1]

            path= "JobSub/"+str(jobID)
            file= "JobSub/"+file
            shutil.move(file,path)

    JobQueue=[]
    jobs= pyslurm.job().get()

    fields =["job_id","name","job_state","run_time_str","num_nodes","nodes","start_time","submit_time"]
    JobQueue.append(fields)
    times=["start_time","submit_time"]
    for key, value in jobs.items():
        JobInQ= []
        for field in fields:
            if field in times:
                print(field)
                JobInQ.append(datetime.utcfromtimestamp(float(value[field])).strftime('%Y-%m-%d %H:%M:%S'))
            else:
                JobInQ.append(value[field])
        JobQueue.append(JobInQ)



    #return HttpResponse("Cleanup time")
    return render(request,'ScriptGen/queue.html',{'queue': JobQueue})


def Results(request):
    # put slurm files where they belong
    for file in os.listdir("JobSub"):
        if file.endswith(".out"):
            jobID= file.split(".")[0]
            jobID= jobID.split("-")[1]
            print("slurm file "+str(jobID))
            path= "JobSub/"+str(jobID)
            file= "JobSub/"+file
            shutil.move(file,path)
            print(file)
    DirList=ListOnlyDirs("JobSub")
    JobFolder=os.getcwd()+"/JobSub/"
    print(DirList)
    return render(request, 'ScriptGen/results.html', {'dirs': DirList,'MainDir':JobFolder})







    return HttpResponse("these are the slurm.out files")
# list the subdirectories
def ListOnlyDirs(path):
    dirlist=[]
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            dirlist.append(filename)
    return dirlist