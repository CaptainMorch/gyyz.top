from django.urls import path

from . import views,ajaxs

app_name = 'doofen'
urlpatterns = [
        path('check/',views.check,name='check'),
        path('exam/',views.exam,name='exam'),
        path('register/',views.register,name='register'),
        path('resetpwd/',views.resetpwd,name='resetpwd'),
        path('resetlink/<str:value>/',views.resetlink,name='resetlink'),
        path('emailsent/',views.emailsent,name='emailsent'),
        path('update/',views.updateexams,name='update_exams'),
        path('report/',views.report,name='report'),
        path('download/',views.download,name='download'),
        path('sumpost/',views.sumpost,name='sumpost'),
        path('summary/',views.summary,name='summary'),
        path('',views.home,name='home'),
        path('ajax/login/',ajaxs.prelogin,name='ajax_login'),
        ]
