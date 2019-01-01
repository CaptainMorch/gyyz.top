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
            nonlocal errors,max_errors
            errors += 1
            self.stdout.write('[Error] {0}(jump{1:d})'.format(msg,errors))
            if errors > max_errors:
                self.stdout.write('Max errors,stop!')
                raise
            return None

        try:
            f = open(os.path.join(settings.BASE_DIR,options['path']),'r')
        except FileNotFoundError:
            error('File Not Found.')
            return

        reader = csv.DictReader(f)
    
        if topic_id != 9:
            full_data = next(reader)
            if full_data['姓名'] != '满分':
                error('the second line must be full score data!')
                return None

            avg_data = next(reader)
            if avg_data['姓名'] != '均分':
                error('the third line must be average score data!')
                return None

        for data in reader:
            class_id = '851001' + str(int(options['grade'])-3) +\
                data['班级'].zfill(3)
            try:
                student = models.Student.objects.get(
                        name=data['姓名'],
                        classnum__class_id=class_id
                        )
            except ObjectDoesNotExist:
                warn('Can\'t find student '+data['姓名'])
                continue

            try:
                exam = models.Exam.objects.get(
                        exam_id=options['exam_id'],
                        classnum=student.classnum
                        )
            except ObjectDoesNotExist:
                error('exam {} not found'.format(options['exam_id']))
            if topic_id == 9:
                exam_subs = exam.get_subjects()
                content = {
                        'stuMixRank':int(data['年排']),
                        'stuMixScore':float(data['总分']),
                        'score':[None]*(len(exam_subs)*2),
                        'stuName':str(student),
                        'classMixRank':None
                        }
                for key in data:
                    if key in exam_subs:
                        index = exam_subs.index(key) * 2
                        try:
                            tmp = float(data[key])
                        except ValueError:
                            tmp = None
                        content['score'][index] = tmp
                    else:
                        tmp = key.replace('年排','')
                        if tmp in exam_subs:
                            index = exam_subs.index(tmp)*2 + 1
                            try:
                                score = float(data[key])
                            except ValueError:
                                score = None
                            content['score'][index] = score
            else:
                content = {
                        'ScoreInfo':{
                            'stuGradeRank':int(data['年排']),
                            'cName':str(student.classnum),
                            'xkName':options['topic'],
                            'stuScore':float(data['总分']),
                            'gradeAvgScore':float(avg_data['总分']),
                            'paperScore':int(full_data['总分']),
                            'stuName':student.name,
                            'stuClassRank':int(data['班排']),
                            },
                        'Performance':{
                            'stuStable':data.get('评价',None),
                            },
                        'LostInfo':{
                            'wrongItemStatInfo':list(),
                            },
                        }
                
                for key in data:
                    if any([b.isnumeric() for b in key]):
                        if data[key] == 'None' or data[key] == full_data[key]:
                            continue
                        try:
                            grade_rate = round(float(avg_data[key])/float(full_data[key]),4)
                        except:
                            raise
                            error('strange data ' +data[key])
                            grade_rate = None
                        info = {
                                'realId':key,
                                'qacq':float(data[key]),
                                'qscore':float(full_data[key]),
                                'gradeScoreRate':grade_rate,
                                'classScoreRate':None,
                                }
                        content['LostInfo']['wrongItemStatInfo'].append(info)
                
            sets = models.Report.objects.filter(
                exam=exam,
                student=student,
                topic=topic_id
                )
            if sets.exists():
                #info('delete existed report.')
                sets.delete()
            models.Report.objects.create(
                    exam=exam,
                    student=student,
                    topic=topic_id,
                    content=dumps(content)
                    )

        f.close()
        return None
