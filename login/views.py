from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from login.forms import *

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
                )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
        variables = RequestContext(request, {
        'form': form
    })
 
    return render(
        request,
        'registration/register.html',
        {'form' : form}
    )
@csrf_protect
def register_success(request):
    return render(
        request,
        'registration/success.html',
        # RequestContext(request)
        )
 
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
@csrf_protect
@login_required
def home(request):
    return render_to_response(
    'home.html',
    { 'user': request.user }
    )
