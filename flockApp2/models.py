from __future__ import unicode_literals

from django.db import models

# Create your models here.



#Group represents on Company us
class Group(models.Model):
    grp_id = models.CharField(max_length=512)
    company = models.CharField(max_length=512)

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
    #1 is us, 2 is user
    by = models.IntegerField(max_length=1)
    ip = models.CharField(max_length=512)

    def __unicode__(self):
        return str(self.text)[:21]


