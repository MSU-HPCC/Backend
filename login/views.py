from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from django.template import RequestContext
from django.shortcuts import render,redirect
from login.forms import *
from login.models import OAuth_ex
import requests

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
    'job_view/jobs.html',
    { 'user': request.user }
    )

def msunet_callback(request):
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')
    print("code : " + code)
    request_url = "https://oauth.itservices.msu.edu/oauth/token?client_id=OAuth-HPCC-HPCC&client_secret=QH7GqwK6bac4AR5gFTQEy6UCBarE6KrKM78GVDMN&grant_type=authorization_code&redirect_uri=https://35.9.22.112/auth/msunet/callback&code=" + code
    print("request_url : " + request_url)
    header = {"Content-type": "application/x-www-form-urlencoded"}
    r = requests.post(request_url, headers=header)
    rjson = r.json()
    access_token = rjson.get('access_token')
    print("access_token : " + access_token)
    if not access_token:
        return redirect('/')

    user_info_url = 'https://oauth.itservices.msu.edu/oauth/me?access_token=' + access_token
    user_info = requests.get(user_info_url)
    user_info_json = user_info.json()
    uid = user_info_json.get('uid')
    name = user_info_json.get('info').get('name')
    email = user_info_json.get('info').get('email')

    msu_users = OAuth_ex.objects.filter(uid = uid, type = '0')
    if msu_users:
        auth_login(request,msu_users[0].user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')

    users = User.objects.filter(email=email)
    if users :
        user = users[0]
    else:
        user = User(username=name, email=email)
        pwd = str('Abc123456')
        user.set_password(pwd)
        user.is_active = True
        user.save()

    oauth_ex = OAuth_ex(user = user,uid = uid,type='0')
    oauth_ex.save()
    auth_login(request,user,backend='django.contrib.auth.backends.ModelBackend')
    return redirect('/')