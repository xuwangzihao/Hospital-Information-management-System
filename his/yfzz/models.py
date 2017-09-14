# coding:utf-8
from __future__ import unicode_literals

from django.db import models

class Hospital(models.Model):
    hid=models.CharField(u'数据库名',max_length=30,unique=True)
    name=models.CharField(u'名称',max_length=30)
    info=models.TextField(u'简介')

    def __unicode__(self):
        return self.name


class Doctor(models.Model):
    did=models.CharField(u'账号',max_length=30,unique=True)
    hospital=models.ForeignKey(Hospital)

    def __unicode__(self):
        return self.did

class Patient(models.Model):
    pid=models.CharField(u'账号',max_length=30,unique=True)
    doctor=models.ForeignKey(Doctor)

    def __unicode__(self):
        return self.pid
	
class Myadmin(models.Model):
    aid=models.CharField(u'账号',max_length=30,unique=True)
    hospital=models.ForeignKey(Hospital)
    #可以属于某个医院或者default
    password=models.CharField(u'密码',max_length=30)
    
    def __unicode__(self):
        return self.aid




































# Create your models here.
