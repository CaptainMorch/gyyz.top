from django.db import models
from django.utils import timezone

class Update(models.Model):
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=10)
    detail = models.TextField(default='空')


class Board(models.Model):
    date = models.DateField(default=timezone.now)
    title = models.CharField(max_length=6,default='公告')
    text = models.TextField()

    def get_summary(self):
        text = self.text
        if len(text) < 10:
            return text
        else:
            return text[:9]+'...'

    class Meta():
        get_latest_by = 'date'


class File(models.Model):
    f = models.FileField()
