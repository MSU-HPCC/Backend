from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse
import os
import io

from . import hpcccreds

import paramiko

import os

from django.views.decorators.csrf import csrf_exempt

from django.core.files.storage import FileSystemStorage
def index(request):
    return HttpResponse("We are at the script generation page")

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NameForm
from .models import ScriptGenInfo
from django.http import JsonResponse
def ScriptGen_create_view(request):
    '''
    form = NameForm(request.POST or None)
    if form.is_valid():
        form.save()
    context={
        'form':form
    }
    return render(request,'ScriptGen/form_create.html',context)'''
    filename = os.getcwd()+ "\ScriptGen\Bash.sb"
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
            bashpath =os.path.join(os.getcwd()+"\ScriptGen", "Bash.sb")
            script = fs.path(name)
            # submit a job
            Success = SubmitJob(bashpath, script, filename)
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
            filename = os.getcwd() + r"\ScriptGen\Bash.sb"
            file = io.open(filename, "w", newline='\n')




            file.write("#!/bin/bash \n\n")
            file.write('##SBATCH Lines for Resource Request ##\n\n')

            file.write("#SBATCH --time=" + str(Wall_time) + "\n")
            file.write("#SBATCH --nodes=" + str(nodes) + "\n")
            file.write("#SBATCH --tasks=" + str(Tasks) + "\n")
            file.write("#SBATCH --mem-per-cpu=" + str(MemoryPerCPu) + "\n")
            file.write("#SBATCH --job-name " + str(job_name) + "\n")
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
        form = NameForm()

    return render(request, 'ScriptGen/name.html', {'form': form})




#code to actually submit a job to hpcc
def SubmitJob(bashpath, script, filename):

    nbytes = 4096
    hostname = hpcccreds.hostname
    port = hpcccreds.port
    username = hpcccreds.username
    password = hpcccreds.password

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    client = paramiko.Transport((hostname, port))
    client.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(client)
    ######## getting working script
    stdin, stdout, stderr = ssh.exec_command("mkdir -p Submissions")
    qsubName = filename.split('.')[0]+'.sb'

    #################################
    #localpath = os.getcwd() + '\ScriptGen\Bash.qsub'
    localpath= bashpath
    filepath = 'Submissions/'+qsubName

    sftp.put(bashpath, filepath)
    localpath= r'C:\Users\zach\Documents\hpcc practice\Classifier.py'
    localpath = script
    filepath = 'Submissions/'+ filename
    sftp.put(script, filepath)
    stdin, stdout, stderr = ssh.exec_command('module load powertools; dev ; mkdir -p Submissions; cd Submissions; pwd; sbatch '+qsubName +'; sq ')
    outlines = stdout.readlines()

    result = ''.join(outlines)
    print(result)
    resultLen= len(result.split())
    if resultLen > 1:

        SuccessStr =result.split()[1]
    else:
        SuccessStr="False"




    sftp.close()
    client.close()
    ssh.close()
    if SuccessStr== "Submitted":
        return True
    else:
        return False
@csrf_exempt
def Update(request):
    text = request.GET.get('text',1)
    FilePreview = text.split("\n")
    #FilePreview=[]
    dictionary = request.GET
    dict2 = request.POST
    #user = request.GET.get('username',1)
    filename = os.getcwd() + "\ScriptGen\Bash.sb"
    #file = open(filename, "w")
    file = io.open(filename, "w", newline='\n')
    file.write(text)
    file.close()
    form = NameForm()
    #return render(request, 'ScriptGen/preview.html', {'preview': FilePreview, 'form': form, 'filePath': filename})
    return render(request,'ScriptGen/download.html')