from django.shortcuts import render
from django.http import HttpResponseNotFound


# Create your views here.
def home(request):
    return render(request,'info/home.html')

def menu(request,menu):
    try:
        response = render(request,'info/{}.html'.format(menu))
    except:
        return HttpResponseNotFound()
    else:
        return response
