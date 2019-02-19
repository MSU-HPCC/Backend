from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import os
import io
from wsgiref.util import FileWrapper
def index(request):
    return HttpResponse("We are at the script generation page")

from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NameForm
from .models import ScriptGenInfo
def ScriptGen_create_view(request):
    '''
    form = NameForm(request.POST or None)
    if form.is_valid():
        form.save()
    context={
        'form':form
    }
    return render(request,'ScriptGen/form_create.html',context)'''
    filename = os.getcwd()+ "\ScriptGen\Bash.sh"
    file = open(filename, "rb")
    response = HttpResponse(file.read())
    response['Content-Disposition'] = 'attachment; filename= ' + 'Bash.sh'

    response['Content-Length'] = os.path.getsize(filename)

    # return response


    return response

    '''
    wrapper = FileWrapper(open((filename),"r"))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response'''



def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            filename = os.getcwd()+ "\ScriptGen\Bash.sh"
            file = io.open(filename,"w",newline='\n')
            CPUs = form.cleaned_data['CPUs']
            Wall_time = form.cleaned_data['Wall_time']
            job_name = form.cleaned_data['job_name']
            script_path = form.cleaned_data['CodeDirectory']
            nodes = form.cleaned_data['nodes']
            #memory = form.cleaned_data['memory']
            MemoryPerCPu = form.cleaned_data['MemoryPerCPU']
            Tasks = form.cleaned_data['Tasks']
            Executable = form.cleaned_data['ExecutableName']
            file.write("#!/bin/bash \n\n")
            file.write('##SBATCH Lines for Resource Request ##\n\n')

            file.write("#SBATCH --time=" + str(Wall_time) + "\n")
            file.write("#SBATCH --nodes=" + str(nodes) + "\n")
            file.write("#SBATCH --tasks=" + str(Tasks) + "\n")
            file.write("#SBATCH --mem-per-cpu=" + str(MemoryPerCPu) + "\n")
            file.write("#SBATCH --job-name " + str(job_name) + "\n")
            file.write("##Command Lines to Run ## \n\n")
            file.write("cd "+str(script_path)+"\n")
            file.write("srun -n "+str(Tasks)+" "+str(Executable)+"\n")

            #file.write("CPUs = "+str(CPUs)+"\n")

            #file.write("Job Name = "+str(job_name)+"\n")
            #file.write("script path = "+str(script_path)+"\n")

            #file.write("memory = "+str(memory)+"\n")
            #file.write("memory = " + str(MemoryPerCPu) + "\n")
            #########

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

            #wrapper = FileWrapper(open(filename, "r"))

           # response = HttpResponse(wrapper, content_type='text/plain')
            #response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
            response['Content-Disposition'] = 'attachment; filename= '+str(filename)

            response['Content-Length'] = os.path.getsize(filename)

            #return response

            return render(request, 'ScriptGen/preview.html', {'preview': FilePreview, 'form': form, 'filePath': filename})
            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'ScriptGen/name.html', {'form': form})



def read_file(request):
    f = open('C:/Users/Zachary Roush.MIHIN-1720/PycharmProjects/DjangoApp/mysite/Bash.sh', 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")
