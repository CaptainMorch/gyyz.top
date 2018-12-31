from django.core.management.base import BaseCommand, CommandError

import datetime
import urllib.request as ur
from json import loads

from doofen.models import Student,Classnum

class Request():
    header_to_send = {
        'Host': 'www.doofen.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'http://www.doofen.com',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Referer': 'http://www.doofen.com/doofen/login.html?',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    } 

    def __init__(self,url):
        self.request = ur.Request(
            url,
            headers = self.header_to_send
            )

        self.response = ur.urlopen(self.request)


    def getJson(self):
        ''' return the dumped obj.'''

        return loads(self.response.read().decode('utf-8'))


class Command(BaseCommand):
    help = 'Update students list.'

    def handle(self,*args,**options):
        for grade in range(16,19):
            for cls in range(1,40):
                cls_id = '851001' + str(grade) + str(cls).zfill(3)
                self.stdout.write('Loading class ' + cls_id + '.')

                stu_url = "http://www.doofen.com/doofen/851001/cls/{}/stu/list".format(cls_id)
                request =  Request(stu_url)
                res_read = request.getJson()

                if not len(res_read):
                    self.stdout.write('Wrong class,break...')
                    break
                self.stdout.write(str(len(res_read)) + ' people in total.')

                classnum = Classnum.objects.get_or_create(
                        class_id = cls_id,
                        grade = str(res_read[0]['stuCode'])[:4]
                        )[0]

                for stu in res_read:
                    student = Student.objects.get_or_create(
                            stu_id=str(stu['stuId']),
                            name=stu['stuName'],
                            classnum=classnum
                            )[0]
                    student.last_update = datetime.date.today()
                    student.save()
        num = Student.objects.filter(
                last_update__date__lt=datetime.date.today()
                ).delete()[0]
        self.stdout.write('Deleted {0:d} students.'.format(num))
