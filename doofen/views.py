from urllib import request as ur
from json import dumps,loads
from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.db.models import ObjectDoesNotExist
from django.http.response import HttpResponseNotFound
import datetime
from django.utils import timezone
from django.core import mail
import random

from . import forms,models
from .student import get_summary
from .connection import Connection
from .classnum import get_exams,update_exams


# Create your views here.
def home(request):
    return render(request,'doofen/home.html')


def check(request):
    if request.method == 'POST':
        form = forms.Student(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            cls_id = '851001{0:d}{1}'.format(
                    int(data['grade'][-2:])-3,
                    data['classnum'].zfill(3)
                    )
            try:
                stu = models.Student.objects.get(
                        name=data['name'],
                        classnum__grade=data['grade'],
                        classnum__class_id=cls_id
                        )
            except ObjectDoesNotExist:
                form.add_error('name','找不到学生信息')
            else:
                if stu.has_passwd:
                    if stu.check_passwd(data['passwd']):
                        request.session['stu_id'] = stu.stu_id

                        #pass
                        return redirect(reverse('doofen:exam'))
                    else:
                        form.add_error('passwd','密码错误')
                else:
                    request.session['stu_id'] = stu.stu_id
                    return redirect(reverse('doofen:register'))
        # Not pass.
        return render(request,'doofen/check.html',{'form':form})
    else:
        form = forms.Student()
        return render(request,'doofen/check.html',{'form':form})


def register(request):
    if 'stu_id' not in request.session:
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = forms.Register(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            stu = models.Student.objects.get(stu_id=request.session['stu_id'])

            stu.set_passwd(data['passwd'])
            stu.email = data['email']
            stu.save()

            return redirect(reverse('doofen:exam'))
        else:
            return render(request,'doofen/register.html',{'form':form})
    else:
        form = forms.Register()
        return render(request,'doofen/register.html',{'form':form})


def resetpwd(request):
    if request.method == 'POST':
        form = forms.ResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            cls_id = '851001{0:d}{1}'.format(
                int(data['grade'][-2:])-3,
                    data['classnum'].zfill(3)
                    )
            try:
                stu = models.Student.objects.get(
                        name=data['name'],
                        classnum__grade=data['grade'],
                        classnum__class_id=cls_id
                        )
            except ObjectDoesNotExist:
                form.add_error('name','找不到学生信息')
            else:
                if stu.has_passwd:
                    if stu.email == data['email']:
                        rand_list = list(range(48,58)) + list(range(65,91))
                        values = [chr(random.choice(rand_list)) for i in range(10)]
                        value = str().join(values)
                        models.ResetLink.objects.create(user=stu,value=value)

                        mail.send_mail(
                                '重置密码验证',
                                '您正在重置您在 www.gyyz.top 处设置的报告查询密码，重置链接两小时内有效。请妥善保管您的新密码。\
                                        http://www.gyyz.top' + reverse('doofen:resetlink',args=(value,)),
                                'captainmorch@gyyz.top',
                                [data['email']],
                                )
                        return redirect(reverse('doofen:emailsent'))
                    else:
                        form.add_error('email','与注册邮箱不符')
                else:
                    form.add_error(None,'该学生未设置密码')
        return render(request,'doofen/resetpwd.html',{'form':form})
    else:
        form = forms.ResetForm()
        return render(request,'doofen/resetpwd.html',{'form':form})

def emailsent(request):
    return render(request,'doofen/emailsent.html')


def resetlink(request,value):
    reset = get_object_or_404(models.ResetLink,value=value)
    dt = timezone.now() - reset.time

    if reset.valid and datetime.timedelta.total_seconds(dt) < 7200:
        reset.valid = False
        reset.save()

        stu = reset.user
        request.session['stu_id'] = stu.stu_id
        stu.clear_passwd()

        return redirect(reverse('doofen:register'))
    else:
        return HttpResponseNotFound()
        

def exam(request):
    context = {}
    if 'stu_id' not in request.session:
        return redirect(reverse('home'))
    else:
        student = models.Student.objects.get(stu_id=request.session['stu_id'])

    if request.method == 'POST':
        exam_id = request.POST['exam_id']
        subjects = loads(request.POST['subjects'])

        exam_ = get_object_or_404(
                models.Exam,
                classnum=student.classnum,
                exam_id=exam_id
                )

        subs = exam_.get_subjects()
        if not subjects:
            subjects = subs

        if all([(s in subs) for s in subjects]):
            request.session['exam_id'] = exam_id
            request.session['subjects'] = subjects
            return redirect(reverse('doofen:report'))
        else:
            return HttpResponseNotFound()
    else:
        exams = get_exams(student.classnum)

        context['update_time'] = student.classnum.exam_update
        context['exams'] = exams
        context['subjects'] = dumps({a['id']:a['subjects'] for a in exams})

        return render(request,'doofen/exam.html',context)


def updateexams(request):
    if 'stu_id' not in request.session:
        return redirect(reverse('home'))
    else:
        student = models.Student.objects.get(stu_id=request.session['stu_id'])

    update_exams(student.classnum)
    return redirect(reverse('doofen:exam'))


def report(request):
    try:
        stu_id = request.session['stu_id']
        exam_id = request.session['exam_id']
        subjects = request.session['subjects']
    except KeyError:
        return redirect(reverse('doofen:home'))

    context = {'data':[]}
    student = models.Student.objects.get(stu_id=stu_id)
    exam_ = models.Exam.objects.get(exam_id=exam_id,classnum=student.classnum)
    connect = Connection(student.classnum)

    context['summary'] = get_summary(student,exam_)
    context['exam_name'] = exam_.name
    context['exam_subs'] = exam_.get_subjects()
    context['report_subs'] = subjects

    for subject in subjects:
        sub_id = models.Exam.sub_table.index(subject)
        try:
            report = models.Report.objects.get(
                    student=student,
                    exam__exam_id=exam_id,
                    topic=sub_id
                    )
        except ObjectDoesNotExist:
            url = "http://www.doofen.com/doofen/851001/report/subjectDatas\
                    ?rId={0}_{1}_{2}".format(sub_id + 1,exam_id,stu_id)
            url_request = ur.Request(url=url,headers=connect.get_header())
            response = ur.urlopen(url_request).read().decode()

            report = models.Report.objects.create(
                    student=student,
                    exam=exam_,
                    topic=sub_id,
                    content=response
                    )
            context['data'].append(loads(response))
        else:
            context['data'].append(loads(report.content))
    return render(request,'doofen/report.html',context)


def download(request):
    pass


def sumpost(request):
    if request.method != 'POST':
        return HttpResponseNotFound()
    if 'stu_id' not in request.session:
        return redirect('home')

    try:
        subs = loads(request.POST['subjects'])
    except ValueError:
        return HttpResponseNotFound()
    else:
        request.session['subjects'] = subs

    return redirect('doofen:summary')


def summary(request):
    try:
        stu_id = request.session['stu_id']
        subjects = request.session['subjects']
    except KeyError:
        return redirect(reverse('doofen:home'))

    context = dict()
    student = models.Student.objects.get(stu_id=stu_id)
    exams = models.Exam.objects.filter(classnum=student.classnum)

    context['summary_exams'] = list(exams.values_list('name',flat=True))
    context['summary_subs'] = subjects
    subjects.append('总分排名')

    temp = {i:{
        'data':[],'xAxis':[],
        'topic_id':i,
        } for i in range(len(subjects))}

    for exam_ in exams:
        try:
            summary = get_summary(student,exam_)
        except ObjectDoesNotExist:
            continue
        
        exam_subs = exam_.get_subjects()
        
        summ = temp[len(subjects)-1]
        summ['data'].append(summary['stuMixRank'])
        summ['xAxis'].append(exam_.name)

        for i in range(len(exam_subs)):
            sub = temp.get(i)
            if sub:
                sub['data'].append(summary['score'][i*2 + 1])
                sub['xAxis'].append(exam_.name)
            
        context['data'] = dumps(list(temp.values()))
        context['topics'] = [{'name':subjects[i],'topic_id':i} for i in range(len(subjects))]
    return render(request,'doofen/summary.html',context)
