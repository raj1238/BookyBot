# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

class BookyBotUser(User):

    step_counter = models.IntegerField(default=0,null=True,blank=True)
    trail_flag = models.IntegerField(default=0,null=True,blank=True)
    v_destination = models.CharField(max_length=100,null=True,blank=True)
    v_source = models.CharField(max_length=100,null=True,blank=True)
    v_date = models.CharField(max_length=100,null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.pk == None:
            self.set_password(self.password)
        super(BookyBotUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "BookyBotUser"
        verbose_name_plural = "BookyBotUsers"

class Booking(models.Model):

    #user = models.ForeignKey(BookyBotUser)
    user = models.ForeignKey(
    BookyBotUser,
    on_delete=models.CASCADE,)
    flight_details = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"     