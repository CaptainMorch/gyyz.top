from django.utils import timezone
from urllib import request as ur
from json import loads
import datetime
from .models import Exam,Student


def get_exams(classnum):
    '''get the exams of given classnum in a list of dict {id,name,subjects:[]}'''

    # Hasn't cache yet.
    if not classnum.exam_update:
        update_exams(classnum)

    exams = Exam.objects.filter(classnum = classnum).order_by('-exam_date')
    return [{
        'id':a.exam_id,
        'name':a.name,
        'subjects':a.get_subjects()
        } for a in exams]


def update_exams(classnum):
    '''request exams from doofen and cache them.'''
    if classnum.exam_update:
        td = timezone.now() - classnum.exam_update
        if datetime.timedelta.total_seconds(td) < 10800:
            return None

    stu_id = Student.objects.filter(classnum=classnum)[0].stu_id
    url = 'http://www.doofen.com/doofen/851001/examsit/student/\
            studentRptData?s={}&p='.format(stu_id)

    response = loads(ur.urlopen(url+'0').read().decode())
    items = response[0]["resultSize"]
    # get length of exams list.

    # request every page and load.
    exams = {}
    for p in range(1,items//10 + bool(items%10) + 1):
        response = loads(ur.urlopen(url+str(p)).read().decode())
        for i in response:
            try:
                exams.setdefault(
                    i['examId'],
                    {'subs':[]}
                    )['subs'].append(i['xkName'])
            except KeyError:
                continue

            exams[i['examId']]['name'] = i['examName']

    # cache into database.
    for exam_id in exams:
        exam_name = exams[exam_id]['name']
        exam_date = datetime.datetime.strptime(
                exam_name.split(sep='_')[-1],
                '%Y%m%d'
                ).date()

        exam = Exam.objects.get_or_create(
                exam_id=exam_id,
                name=exam_name,
                classnum=classnum,
                exam_date=exam_date
                )[0]
        exam.set_subjects(exams[exam_id]['subs'])

    classnum.exam_update = timezone.now()
    classnum.save()

    return None
