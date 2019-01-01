from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from json import dumps
import os,csv

from doofen import models


class Command(BaseCommand):
    help = 'import data from a csv file.'

    def add_arguments(self,parser):
        parser.add_argument(
                'path',
                type=str,
                help='path to a csv file (from project root)'
                )
        parser.add_argument(
                'topic',
                type=str,
                help='choose from "语文","数学","英语"......"地理","总览"'
                )
        parser.add_argument(
                'exam_id',
                type=str,
                help='id of the target exam'
                )
        parser.add_argument(
                'grade',
                type=str,
                help='example:19'
                )

    def handle(self,*args,**options):
        errors = 0
        max_errors = 10
        sub_table = ['语文','数学','英语','物理','化学','政治','历史','地理','生物','总览',]
        topic_id = sub_table.index(options['topic'])

        def info(msg):
            self.stdout.write('[Info] '+msg)
            return None

        def warn(msg):
            self.stdout.write('[Warn] '+msg)
            return None

        def error(msg):
            errors += 1
            self.stdout.write('[Error] {0}(jump{d:1})'.format(msg,errors))
            if errors > max_errors:
                self.stdout.write('Max errors,stop!')
                raise
            return None

        try:
            f = open(os.path.join(settings.BASE_DIR,options['path']),'rb')
        except FileNotFoundError:
            error('File Not Found.')
            return

        reader = csv.DictReader(f)
    
        full_data = reader.next()
        if full_data['姓名'] != '满分':
            error('the second line must be full score data!')
            return None

        avg_data = reader.next()
        if avg_data['姓名'] != '均分':
            error('the third line must be average score data!')
            return None

        for data in reader:
            class_id = '851001' + str(int(options['grade']-3)) +\
                data['班级'].zfill(3)
            try:
                student = models.Student.objects.get(
                        name=data['姓名'],
                        classnum__id=class_id
                        )
            except ObjectDoesNotExist:
                warn('Can\'t find student '+data['姓名'])
                continue

            try:
                exam = models.Exam.objects.get(
                        exam_id=options['exam-id'],
                        classnum=student.classnum
                        )
            except ObjectDoesNotExist:
                error('exam {} not found'.format(options['exam_id']))
            if topic_id == 9:
                content = {
                        'stuMixRank':data['年排'],
                        'stuMixScore':data['总分'],
                        'score':[None]*len(exam.get_subjects*2),
                        'stuName':str(student),
                        'classMixRank':None

                        }
                for key in data:
                    if key in sub_table:
                        index = sub_table.index(key) * 2
                        content['scores'][index] = data[key]
                    else:
                        tmp = key.replace('年排','')
                        if tmp in sub_table:
                            index = sub_table.index(tmp)*2 + 1
                            content['score'][index] = data[key]
            else:
                content = {
                        'ScoreInfo':{
                            'stuGradeRank':data['年排'],
                            'cName':str(student.classnum),
                            'xkName':options['topic'],
                            'stuScore':data['总分'],
                            'gradeAvgScore':avg_data['总分'],
                            'paperScore':full_data['总分'],
                            'stuName':student.name,
                            'stuClassRank':data['班排'],
                            },
                        'Performance':{
                            'stuStable':data.get('评价',None),
                            },
                        'LostInfo':{
                            'wrongItemStatInfo':[,],
                            },
                        }
                
                for key in data:
                    if any([b.isnumeric() for b in key]):
                        try:
                            grade_rate = (float(data[key])/avg_data[key]).round(4)
                        except:
                            warn('strange data ' +data[key])
                            grade_rate = None
                        info = {
                                'realId':key,
                                'qacq':data[key],
                                'qscore':full_data[key],
                                'gradeScoreRate':grade_rate,
                                }
                        content['LostInfo']['wrongItemStatInfo'].append(info)
                
            sets = models.Report.objects.filter(
                exam=exam,
                student=student,
                topic=topic_id
                )
            if sets.exist():
                warn('delete existed report.')
                sets.delete()
            models.Report.objects.create(
                    exam=exam,
                    student=student,
                    topic=topic_id,
                    content=dumps(content)
                    )

        f.close()
        return None
