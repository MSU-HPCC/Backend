from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import os
import io
import subprocess as sub
import paramiko
import os
import time
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@login_required
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
import subprocess

@login_required
def ScriptGen_create_view(request):
    ''' This function isn't used, it was made to test file download'''
    filename = os.getcwd()+ "/ScriptGen/Bash.sb"

    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' + 'Bash.sb'

    response['Content-Length'] = os.path.getsize(filename)

    # return response


    return response


@login_required
def SlurmFile(request):
    '''this function travels to the home/user directory where jobs are submitted
     and locates a specific directory named JobId+JobName . it downloads that slurm.out file. thats the output file for a job. this function is actually called from a template'''
    dir = request.GET.get('dir','')
    user = request.user.username
    jobid = dir.split("-")[1]
    slurmName= "slurm-"+str(jobid)+".out"
    filename = "/home/"+user+"/"+dir+"/"+slurmName
    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' +"slurm-"+str(jobid)+".out"

    response['Content-Length'] = os.path.getsize(filename)

    # return response

    return response
    return HttpResponse("ok")

@login_required
def downloadFile(request):
    ''' this function isn't used, it was just to test file downlad'''
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']

        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'ScriptGen/download.html', context)

@login_required
@csrf_exempt
def get_name(request):
    '''This view function handles the script gen page. it takes the
 options inputted by the user and writes the bash script from that. The Bash script is always the same file, its just rewritten copied and moved. '''
    SubmittedJob = False
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = NameForm(request.POST)
        #if request.POST.get('action') == "Update Bash Script":
        
        form = NameForm(request.POST)
        # file upload
        if request.FILES:
            #script_path = form.cleaned_data['CPUs']
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

            #job_name = form.cleaned_data['job_name']
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

@login_required
def SubmitJob(bashpath, script, filename,user):
    '''
    This function submites a job. it needs the filepath of the bashfile, the script you want to run, and the username. it travels to home/user and submits
    the job through the command line by doing 'sbatch Bash.sh'. it aslso makes
    the directories where slurm.out fies are stored
    '''
    currDir = os.getcwd()
    #go into jobsub folder to execute batch script
    os.chdir("/home/"+user)
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

    # get the jobid so we know what folder to put the files in


    try:
        command ="sbatch " + BashScriptName
        #result = subprocess.check_output(["sbatch", BashScriptName])
        #print(command)
        result = subprocess.check_output(["runuser","-l",user,"-c",command])

        #print(result)
        result = result.split()[-1]
        jobid = int(result)

        #jobid = a.submit_batch_job({'script': BashScriptName})

        #print(jobid)
        time.sleep(0.3)
        #print("done")
        #print("Job Name is "+str(jobName))


    except Exception:
        os.chdir(currDir)

        return False

    #print("jobid = "+str(jobid))
    # make the directory with full permisions
    # it will be named after the jobid
    job_name = pyslurm.job().get()[jobid]['name']
    newDir = str(job_name)+"-"+str(jobid)
    #print("Dir created: "+newDir)
    os.mkdir(str(newDir), mode=0o777)
    # move the bash script, actual script, and slurm.out to new folder jobid
    # if jobid=13, the folder is named 13
    #shutil .move(BashScriptName, str(jobid))
    #shutil.move(filename, str(jobid))
    slurmname= "slurm-"+str(jobid)+".out"


    if os.path.isfile(slurmname):
        #print("slurm file exists")
        shutil.move(slurmname, str(newDir))
    shutil.move(BashScriptName, str(newDir))
    time.sleep(0.3)
    shutil.copy(filename, str(newDir))

    #shutil.move(filename, str(jobid))
    # go back to original directory not to fuck with anything
    os.chdir(currDir)







    return True

@login_required
@csrf_exempt
def Update(request):
    ''' this function isnt used'''
    #print("we are updating")
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

@login_required
def CleanUp(request):
    ''' this function actually collects the personal job queue.it finds all the recent jobs that are yours and creates a 2d matrix for the job queue
    this is then passed to the template to be rendered. '''
    username = request.user.username

    JobQueue=[]
    jobs= pyslurm.job().get()
    AllJobs = pyslurm.slurmdb_jobs().get()
    fields =["job_id","user","name","job_state","run_time_str","num_nodes","nodes","start_time","submit_time"]
    JobQueue.append(fields)
    times=["start_time","submit_time"]
    for key, value in jobs.items():
        JobInQ= []
        jobid = value["job_id"]
        for field in fields:
            if field in times:
                temp_time = float(value[field])
                if  temp_time < 10000:#Check for uninitialized time Added 4-20-19
                    JobInQ.append("0000-00-00 00:00:00")
                else:
                    JobInQ.append(datetime.utcfromtimestamp(float(value[field])).strftime('%Y-%m-%d %H:%M:%S'))
                #JobInQ.append(datetime.utcfromtimestamp(float(value[field])).strftime('%Y-%m-%d %H:%M:%S'))
            elif field=="user":
                if jobid in AllJobs:
                    jobid = value["job_id"]
                    user = AllJobs[jobid]['user']
                    JobInQ.append(user)
                else:
                    for jobid2 in AllJobs:
                        if value['user_id'] == AllJobs[jobid2]['gid']:
                            user = AllJobs[jobid2]['user']
                            JobInQ.append(user)
                            break
            else:
                JobInQ.append(value[field])
        EntryUser= JobInQ[1]
        #print(EntryUser)
        if EntryUser == username:
            JobQueue.append(JobInQ)



    #return HttpResponse("Cleanup time")
    return render(request,'ScriptGen/queue.html',{'queue': JobQueue})

@login_required
def Results(request):
    '''
    This helps render the results page. everytime its called it moves slurm.out files to their respective 
    folders if they havent already. it then collects the names of all the finished directories and passes it to the template. the template then calls a 
    SlurmFile function to download the output file.
    '''
    # put slurm files where they belong
    # clean up the directories

    dirs= []
    files=[]
    #JobTable= pyslurm.slurmdb_jobs().get()
    user = request.user.username
    mypath = '/home/'+user
    #grab all the dirs and filenames aka slurm.outfiles and directories
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        files.extend(filenames)
        dirs.extend(dirnames)
        break
    # for all the files in the users directory
    for f in files:
        # if its a slurm.out file
        if "slurm-" in f:
            jobid = f.split("-")[1].split(".")[0]
            for d in dirs:
                dirJobID = d.split("-")[1]
                if jobid==dirJobID:
                    DirName = mypath+"/"+d
                    f = mypath+"/"+f
                    shutil.move(f,DirName)
           # jobid = int(jobid)
            # fixes weird error
    #done putting files back where they need to be
    ##########################################


    DirList=[]
    for d in dirs:
        jobid = d.split("-")[1]
        slurmname = "slurm-" + jobid + ".out"
        slurmfile = mypath + "/" + d + "/" + slurmname
        if os.path.exists(slurmfile):
            DirList.append(d)

    #JobFolder=os.getcwd()+"/JobSub/"

    return render(request, 'ScriptGen/results.html', {'dirs': DirList})







    return HttpResponse("these are the slurm.out files")

# list the subdirectories
@login_required
def ListOnlyDirs(path):
    ''' never used'''
    dirlist=[]
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            dirlist.append(filename)
    return dirlist


@login_required
def Test(request):
    ''' never used'''
    filename = '/home/roushzac//wNdCiHi3-5530/slurm-5530.out'
    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' + 'slurm.out'

    response['Content-Length'] = os.path.getsize(filename)

    # return response

    return response
