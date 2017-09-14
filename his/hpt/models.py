# coding:utf-8
from __future__ import unicode_literals

from django.db import models

class Doctor(models.Model):
    did=models.CharField(u'账号',max_length=30,unique=True)
    password=models.CharField(u'密码',max_length=30)
    name=models.CharField(u'姓名',max_length=30)
    info=models.TextField(u'简介')
    pcnt=models.IntegerField(u'患者数',default=0)
    def __unicode__(self):
        return self.did

class Patient(models.Model):
    pid=models.CharField(u'账号',max_length=30,unique=True)
    password=models.CharField(u'密码',max_length=30)
    name=models.CharField(u'姓名',max_length=30)
    info=models.TextField(u'简介')
    doctor=models.ForeignKey(Doctor)
    is_changing=models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.pid

class Message(models.Model):
    mid=models.CharField(u'账号',max_length=30)
    fromhid=models.CharField(u'来自哪个医院',max_length=30)
    fromdid=models.CharField(u'来自哪个医生',max_length=30)
    tohid=models.CharField(u'转到哪个医院',max_length=30)
    todid=models.CharField(u'转到哪个医生',max_length=30)
    pid=models.CharField(u'来自哪个患者',max_length=30)
    title=models.CharField(u'标题',max_length=30)
    info=models.TextField(u'详情')
    extra = models.TextField(u'附加信息',default='')
    pub_time=models.DateTimeField(u'发布时间',auto_now_add=True)
    
    type=models.CharField(u'类型',max_length=1)
    '''
			0 block
			1 患者提交的转院申请 (from: self patient) (to: self doctor) (contain: name,pid,reason) (two select:deny 2,ok 3)
			2 医生拒绝(from: self doctor) (to: self patient) (contain: reason) (two select:deny 1,ok 0)
			3 医生提交的转院申请 (from: self doctor) (to: another hospital) (contain: name,pid,hid,did,reason) (zero select:if(病人还没有转过来):4*2,if(所有的医生都拒绝了):7)
			4 医院分配医生申请 (from: another hospital) (to: another doctor) (contain: name,pid,hid,did,reason) (two select:deny 3,ok 5)
			5 医生同意转院申请 (from: another doctor) (to: another hospital) (contain: name,pid,hid,did,success) (zero select:if(病人不处于转诊状态):8,else 6)
			6 转诊成功通知 (from: another hospital) (to: self patient,self doctor) (contain: name,pid,hid,did,success) (one select:ok 0)
			7 转诊失败通知 (from: another hospital) (to: self patient,self doctor) (contain: name,pid,hid,list of reason) (one select:ok 0)
			8 病人已经不处于转诊状态通知 (from: another hospital) (to: another doctor) (contain: name,pid,hid,did,error) (one select:ok 0)
	'''
    
    
    def __unicode__(self):
        return self.title








# Create your models here.
