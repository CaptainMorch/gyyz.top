from random import randrange
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from json import loads,dumps
import urllib.request as ur

from .models import Session,TeacherAccount


class Connection():
    header_send = {
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
        }  # define Head

    def __init__(self,classnum):
        self.classnum = classnum
        return None

    def get_header(self):
        session = self.get_session()
        self.header_send['cookie'] = 'JSESSIONID=' + session
        return self.header_send

    def login(self):
        try:
            # try to load account of specified class
            account = TeacherAccount.objects.get(classnum=self.classnum)
        except ObjectDoesNotExist:
            # get a randomtic account 
            accounts = TeacherAccount.objects.all()
            account = accounts[randrange(accounts.count())]

        data_send = {
                "username":account.username,
                "password":account.password
                }
        data_send = str(data_send).encode("utf-8")
        # generate request body

        request = ur.Request(
            url = "http://www.doofen.com/doofen/sys/login",
            data = data_send,
            headers = self.header_send)
        response = ur.urlopen(request)
        # send login request

        info = response.info()
        for each in info['Set-Cookie'].split(';'):
            if each.find('JSESSIONID')+1:
                sessionid = each.split('=')[1]
        # get session id
        response = response.read().decode()

        if response.find("\"success\":true") == -1 :
            raise ValueError("Can't log in!")

        return sessionid


    def get_session(self):
        try:
            latest = Session.objects.filter(
                    classnum=self.classnum).latest('last_use')
        except ObjectDoesNotExist:
            td = timedelta(1,0,0)
        else:
            td = timezone.now() - latest.last_use

        if timedelta.total_seconds(td) > 1200:
            session = self.login()
            latest = Session.objects.create(
                    content=session,
                    classnum=self.classnum
                    )

        latest.last_use = timezone.now()
        latest.save()
        return latest.content

