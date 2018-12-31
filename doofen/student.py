from json import loads

from .exam import load_summary
from .models import Report

def get_summary(student,exam):
    '''get summary of the given student in given exam.'''

    load_summary(exam)
    report = Report.objects.get(
            student=student,
            exam=exam,
            topic=9
            )

    return loads(report.content)
