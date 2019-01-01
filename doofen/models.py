from django.utils import timezone
from django.db import models
from json import loads
from urllib import request as ur
import hashlib

import secrets
# Create your models here.

class Student(models.Model):
    stu_id = models.CharField(max_length=16,unique=True)
    passwd_md5 = models.CharField(null=True,max_length=32)
    email = models.EmailField(null=True)
    name = models.CharField(max_length=10)
    classnum = models.ForeignKey('Classnum',on_delete=models.CASCADE)
    last_update = models.DateField(null=True)

    def __str__(self):
        return str(self.classnum) + self.name

    def get_digest(self,passwd):
        m = hashlib.md5()
        m.update(passwd.encode())
        salt = secrets.SALT + self.name
        m.update(salt.encode())

        return m.hexdigest()

    def set_passwd(self,passwd):
        self.passwd_md5 = self.get_digest(passwd)
        self.save()

    def check_passwd(self,passwd):
        d = self.get_digest(passwd)
        return d == self.passwd_md5

    def clear_passwd(self):
        self.passwd_md5 = None
        self.save()

    @property
    def has_passwd(self):
        return bool(self.passwd_md5)


class Classnum(models.Model):
    class_id = models.CharField(max_length=12,unique=True)
    grade = models.CharField(max_length=4)
    exam_update = models.DateTimeField(null=True)

    def __str__(self):
        return '{0:d}届{1:d}班'.format(
                int(self.grade[-2:]),
                int(self.class_id[-2:])
                )


class Exam(models.Model):
    exam_id = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    subjects = models.IntegerField(default=0)
    summary_subs = models.IntegerField(default=0)
    classnum = models.ForeignKey('Classnum',on_delete=models.CASCADE)
    exam_date = models.DateField(null=True)

    sub_table = ['语文','数学','英语','物理','化学','政治','历史','地理','生物']

    def __str__(self):
        return self.name

    def set_subjects(self,subjects):
        subs = 0
        for sub in subjects:
            subs += pow(2,self.sub_table.index(sub))
        self.subjects = subs
        self.save()
        return None
        
    def get_subjects(self):
        subs = bin(self.subjects)[:1:-1].ljust(9).replace(' ','0')
        sub_list = []

        for b in range(len(subs)):
            if int(subs[b]):
                sub_list.append(self.sub_table[b])
        return sub_list


class Report(models.Model):
    student = models.ForeignKey('Student',on_delete=models.CASCADE)
    exam = models.ForeignKey('Exam',on_delete=models.CASCADE)
    topic = models.IntegerField()
    content = models.TextField()
    add_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.student) + str(self.exam) + str(self.topic)

    class Meta:
        unique_together = ('student','exam','topic')

class Session(models.Model):
    create_time = models.DateTimeField(default=timezone.now)
    last_use = models.DateTimeField(null=True,default=None)
    content = models.CharField(max_length=32)
    classnum = models.ForeignKey('Classnum',on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.last_use)


class ResetLink(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('Student',on_delete=models.CASCADE)
    value = models.CharField(max_length=11)
    valid = models.BooleanField(default=True)


class TeacherAccount(models.Model):
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=32)
    classnum = models.ForeignKey('Classnum',on_delete=models.CASCADE)
