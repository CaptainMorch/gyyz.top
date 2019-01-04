from urllib import request as ur
from json import dumps,loads
from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.db.models import ObjectDoesNotExist
from django.http.response import FileResponse,HttpResponseNotFound
from django.conf import settings
import datetime
from django.utils import timezone
from django.core import mail
import random
import io

import xlsxwriter

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


def report(request,to_context=False):
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

    context['student_name'] = str(student)
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
    if to_context:
        return context
    else:
        return render(request,'doofen/report.html',context)


def download(request):
    class Pointer:
        def __init__(self,max_width):
            '''Notice:max_width is zero-indexed.'''
            self.column = -1
            self.row = -1
            self.max_width = max_width

        def get_cell(self,in_line=False,line_gap=1):
            if in_line and self.column < self.max_width:
                self.column += 1
                return (self.row,self.column)
            else:
                self.row += line_gap
                self.column = 0
                return (self.row,self.column)

        def get_row(self):
            self.row += 1
            self.column = -1
            return (self.row,0,self.row,self.max_width)

        def skip_row(self,rows=1):
            self.row += rows
            self.column = -1
            return None

    data = report(request,to_context=True)

    if not isinstance(data,dict):
        return data

    output = io.BytesIO()

    wb = xlsxwriter.Workbook(output,{'tmpdir':settings.TEMP_DIR})
    fm_title = wb.add_format({
        'font_name':'微软雅黑',
        'font_size':24,
        'align':'center',
        'valign':'vcenter',
        'shrink':True,
        })
    fm_subtitle = wb.add_format({
        'font_name':'等线',
        'font_size':20,
        'align':'center',
        'valign':'center',
        })
    fm_header = wb.add_format({
        'font_name':'微软雅黑',
        'font_size':12,
        'align':'center',
        'valign':'center',
        })
    fm_value = wb.add_format({
        'font_name':'微软雅黑',
        'num_format':'0.0',
        'font_size':10,
        'align':'center',
        'valign':'vjustify',
        'text_wrap':True
        })
    fm_value_gray = wb.add_format({
        'font_name':'微软雅黑',
        'num_format':'0.0',
        'font_size':10,
        'align':'center',
        'valign':'vjustify',
        'text_wrap':True,
        'bg_color':'#F2F2F2'
        })

    ws = wb.add_worksheet('数据')
    ws.set_paper(9)
    ws.center_horizontally()
    ws.set_margins(left=0.4,right=0.4,top=0.5,bottom=0.5)
    ws.set_footer('&C第 &P 页')
    ws.hide_gridlines(1)
    ws.fit_to_pages(1,0)

    pointer = Pointer(6)

    ws.merge_range(
            *pointer.get_row(),
            data['exam_name'],
            fm_title
            )
    ws.set_row(pointer.row,50)
    ws.merge_range(
            *pointer.get_row(),
            data['student_name'],
            fm_header
            )
    pointer.skip_row(22)

    summary_ = [
            ['总分',data['summary']['stuMixScore']],
            ['年排',data['summary']['stuMixRank']],
            ['班排',data['summary'].get('classMixRank')],
            ]
    for sub in data['data']:
        summary_.append([
            sub['ScoreInfo']['xkName'],
            sub['ScoreInfo']['stuScore'],
            ])
    for each in summary_:
        ws.write_column(
            *pointer.get_cell(in_line=True,line_gap=2),
            each,
            fm_header
            )
    pointer.skip_row(2)

    for sub in data['data']:
        info = sub['ScoreInfo']
        ws.merge_range(
                *pointer.get_row(),
                '————{}————'.format(info['xkName']),
                fm_subtitle
                )
        ws.set_row(pointer.row,25)
        ws.write_row(
                *pointer.get_cell(),
                ['得分','满分','班排','年排','班级均分','年级均分','评价'],
                fm_header
                )
        ws.write_row(
                *pointer.get_cell(),
                [
                    info.get('stuScore'),
                    info.get('paperScore'),
                    info.get('stuClassRank'),
                    info.get('stuGradeRank'),
                    info.get('classAvgScore'),
                    info.get('gradeAvgScore'),
                    sub['Performance'].get('stuStable')
                    ],
                fm_value
                )
        pointer.skip_row()
 
        ws.write_row(
                *pointer.get_cell(in_line=False),
                ['题号','题型','得分','满分','班级均分','年级均分','知识点'],
                fm_header
                )
        items = sub['LostInfo'].get('wrongItemStatInfo')
        if items:
            for i in range(len(items)):
                item = items[i]
                try:
                    cls_score = item.get('classScoreRate')*item.get('qacq')
                except TypeError:
                    cls_score = None
                try:
                    grade_score = item.get('gradeScoreRate')*item.get('qacq')
                except TypeError:
                    grade_score = None

                ws.write_row(
                        *pointer.get_cell(),
                        [
                            item.get('realId'),
                            item.get('topicName'),
                            item.get('qacq'),
                            item.get('qscore'),
                            cls_score,
                            grade_score,
                            item.get('realTopicName'),
                            ],
                        fm_value if i%2 else fm_value_gray
                        )
        pointer.skip_row()

    ws.print_area(0,0,pointer.row,pointer.max_width)
    ws.set_column(0,pointer.max_width,12)
    wb.close()

    output.seek(0)
    response = FileResponse(
            output,
            as_attachment=True,
            filename='{0}_{1}.xlsx'.format(
                data['student_name'],
                data['exam_name']
                )
            )
    return response


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
