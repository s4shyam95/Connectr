"""flockProj2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from flockApp2.views import *
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'listen/', listen),
    url(r'configure/', configure),
    url(r'callback/', callback),
    url(r'voice/', voice),
    url(r'client/', client),
    url(r'naya_grp/', new_group),
    url(r'naya_msg/', new_message),
]
