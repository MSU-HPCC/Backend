from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_protect
@csrf_protect
@login_required
def index(request):
    return HttpResponseRedirect('/ScriptGen/jobqueue')
