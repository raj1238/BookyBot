# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import Group, User
from BookyBotApp.models import *

# Register your models here.

admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User)
admin.site.register(Group)
admin.site.register(BookyBotUser)
admin.site.register(Booking)
