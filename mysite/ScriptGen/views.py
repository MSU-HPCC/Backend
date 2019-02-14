from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import os
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
    filename = "C:/Users/Zachary Roush.MIHIN-1720/PycharmProjects/DjangoApp/mysite/Bash.sh"
    wrapper = FileWrapper(open((filename),"r"))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(filename)
    response['Content-Length'] = os.path.getsize(filename)
    return response
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
            filename = os.getcwd()+ "\Bash.sh"
            file = open(filename,"w")
            CPUs = form.cleaned_data['CPUs']
            Wall_time = form.cleaned_data['Wall_time']
            job_name = form.cleaned_data['job_name']
            script_path = form.cleaned_data['script_path']
            nodes = form.cleaned_data['nodes']
            memory = form.cleaned_data['memory']
            MemoryPerCPu = form.cleaned_data['MemoryPerCPU']
            file.write("CPUs = "+str(CPUs)+"\n")
            file.write("Wall Time = "+str(Wall_time)+"\n")
            file.write("Job Name = "+str(job_name)+"\n")
            file.write("script path = "+str(script_path)+"\n")
            file.write("nodes = "+str(nodes)+"\n")
            file.write("memory = "+str(memory)+"\n")
            file.write("memory = " + str(MemoryPerCPu) + "\n")
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
            response['Content-Disposition'] = 'attachment; filename= Bash.sh'

            response['Content-Length'] = os.path.getsize(filename)

            #return response
            return render(request, 'ScriptGen/preview.html', {'preview': FilePreview, 'form': form})
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