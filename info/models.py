from django.db import models

# Create your models here.
class University(models.Model):
    full_name = models.CharField('全称',max_length=16,unique=True)
    short_name = models.CharField('简称',max_length=8,unique=True)
    location = models.CharField('地址',max_length=32)
    is_985 = models.BooleanField('属于985院校')
    is_211 = models.BooleanField('属于211院校')
    is_syl = models.BooleanField('属于双一流')
    official_site = models.URLField('官网网址')
    admittion_site = models.URLField('招生官网网址',null=True)
    qs_global_rank = models.IntegerField('QS世界排名',null=True)
    qs_china_rank = models.IntegerField('QS全国排名',null=True)
    extra = models.TextField('详细信息',default='')

    def __str__(self):
        return self.full_name

class AdmissionData(models.Model):
    SUBJECTS = [(0,'全部'),(1,'文科'),(2,'理科')]

    university = models.ForeignKey(
            'University',
            on_delete=models.CASCADE,
            verbose_name='院校'
            )
    year = models.IntegerField('年份')
    region = models.CharField('招生地区',max_length=8,default='贵州')
    subject = models.IntegerField('文理科',choices=SUBJECTS)
    count = models.IntegerField('录取数')
    mark_max = models.IntegerField('最高录取')
    mark_min = models.IntegerField('最低录取')
    mark_average = models.IntegerField('录取均分',null=True)

    def __str__(self):
        return self.university.short_name + str(self.year) + self.get_subject_display()

class DiscussGroup(models.Model):
    university = models.ForeignKey(
            'University',
            on_delete=models.CASCADE,
            verbose_name='院校'
            )
    name = models.CharField('名称',max_length=16)
    group_type = models.BooleanField('平台',choices=[(True,'QQ'),(False,'微信')])
    group_id = models.CharField('群号',max_length=16)
    add_date = models.DateField(auto_now=True)
    qr_code = models.ImageField('二维码',null=True)

    def __str__(self):
        return self.university.full_name

class Item(models.Model):
    title = models.CharField(max_length=16)
    url = models.URLField()
    add_date = models.DateField(auto_now=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
