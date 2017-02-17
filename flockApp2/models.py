from __future__ import unicode_literals

from django.db import models

# Create your models here.


class IPMan(models.Model):
    ip = models.CharField(max_length=512)
    name = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name


#Group represents on Company us
class Group(models.Model):
    grp_id = models.CharField(max_length=512)
    company = models.CharField(max_length=512)
    group_name = models.CharField(max_length=512)

    def __unicode__(self):
        return self.company

class User(models.Model):
    user_id = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    grp = models.ForeignKey(Group, null=True)

    def __unicode__(self):
        return self.access_token

class Chat(models.Model):
    text = models.CharField(max_length=512)
    grp = models.ForeignKey(Group)
    by = models.IntegerField(max_length=1)
    ip = models.CharField(max_length=512)
    ipman = models.ForeignKey(IPMan)

    def __unicode__(self):
        return str(self.text)[:21]


class Log(models.Model):
    text = models.CharField(max_length=2048)



