from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    return HttpResponse("You are at Zach's homepage")