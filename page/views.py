import os

from django.shortcuts import render,redirect
from django.http import Http404
from django.conf import settings
from django.core.mail import EmailMultiAlternatives 

from .models import Update,Board

# Create your views here.

def static(request,page):
    file_path = '{0}page/{1}.html'.format(settings.STATIC_ROOT,page)
    if os.path.isfile(file_path):
        return render(request,page+'.html')
    else:
        raise Http404()

def home(request):
    if request.method == 'POST':
        subject, from_email, to = '新的回复', 'captainmorch@gyyz.top', 'captainmorch@qq.com'
        text_content = request.POST.get('words') 
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.send()
        return redirect('/')
    else:
        board = Board.objects.latest()
        updates = Update.objects.all()
        days = updates.dates('date','day')
        
        dates = list()
        for date in days:
            tmp = {'date':date}
            tmp['updates'] = updates.filter(date=date)
            dates.append(tmp)

        dates.reverse()

        return render(request, 'home.html',{'dates':dates,'board':board})

     
