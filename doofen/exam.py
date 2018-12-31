from urllib import request as ur
from json import loads,dumps

from .models import Session,Report,Student
from .connection import Connection


def load_summary(exam):
    '''load summary of given exam.
    return True if request from foofen,
    False if from cache.
    '''

    if exam.subjects != exam.summary_subs:
        Report.objects.filter(topic=9,exam=exam).delete()

        connect = Connection(exam.classnum)
        url = "http://www.doofen.com/doofen/851001/rpt100/1001\
            ?clsId={0}&examId={1}".format(
                    exam.classnum.class_id,
                    exam.exam_id
                    )
        request = ur.Request(url,headers=connect.get_header())
        response = ur.urlopen(request).read().decode()

        scores = loads(response)[0]['stuScore']
        for i in range(len(scores)):
            student = Student.objects.get(stu_id=scores[i]['stuId'])
            content = scores[i]
            content.update({'classMixRank':i+1})
            Report.objects.create(
                    student=student,
                    topic=9,
                    content=dumps(content),
                    exam=exam
                    )

        exam.summary_subs = exam.subjects
        exam.save()
        return True
    else:
        return False
