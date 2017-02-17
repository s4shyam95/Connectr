from django.contrib import admin
from flockApp2.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Chat)
admin.site.register(IPMan)
admin.site.register(Log)