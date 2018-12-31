from django.core.management.base import BaseCommand, CommandError

from doofen .models import Report


class Command(BaseCommand):
    help = 'Delete all caches of given exam id.'

    def add_arguments(self,parser):
        parser.add_argument('exam_id')


    def handle(self,*args,**options):
        objs = Report.objects.filter(exam__exam_id=options['exam_id'])
        num = objs.delete()[0]

        self.stdout.write('Cleared {} reports.'.format(num))
