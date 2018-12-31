"""gyyz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path
from django.views.generic import TemplateView

from page import views

urlpatterns = [
    path('captcha/',include('captcha.urls')),
    path('doofen/', include('doofen.urls')),
    path('info/', include('info.urls')),
    path('app/', TemplateView.as_view(template_name='app.html'),name='app'),
    path('<str:page>/', views.static, name='static_page'),
    path('captain/morch/', admin.site.urls),
    path('', views.home, name='home'),
]
