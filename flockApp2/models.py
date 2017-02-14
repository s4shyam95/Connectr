from __future__ import unicode_literals

from django.db import models

# Create your models here.


#Group represents on Company us
class Group(models.Model):
    grp_id = models.CharField(max_length=128)
    company = models.CharField(max_length=128)
    #token required to send to this group
    token = models.CharField(max_length=512)

    def __unicode__(self):
        return self.company

class Chat(models.Model):
    text = models.CharField(max_length=512)
    #1 is us, 2 is user
    by = models.IntegerField(max_length=1)
    ip = models.CharField(max_length=128)

    def __unicode__(self):
        return str(self.text)[:21]


