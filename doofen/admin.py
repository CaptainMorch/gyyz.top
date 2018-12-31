from django.contrib import admin

from .models import Student,ResetLink,Classnum,Exam,Report,Session
# Register your models here.


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('exam','add_date','student','topic',)
    list_per_page = 50


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name','classnum')


admin.site.register([Student,Classnum,ResetLink,Session])
