# coding:utf-8
"""his URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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

from yfzz import views as yfzz_views

urlpatterns =[
    url(r'^$',yfzz_views.home,name='home'),
    url(r'^test$',yfzz_views.test,name='test'),

    url(r'^adminlogin$',yfzz_views.adminlogin,name='adminlogin'),
    url(r'^adminlogout$',yfzz_views.adminlogout,name='adminlogout'),
    url(r'^adminhomepage$',yfzz_views.adminhomepage,name='adminhomepage'),

    url(r'^doctorinsert$',yfzz_views.doctorinsert,name='doctorinsert'),
    url(r'^doctordelete$',yfzz_views.doctordelete,name='doctordelete'),
    url(r'^doctorchange$',yfzz_views.doctorchange,name='doctorchange'),
    url(r'^doctorlist',yfzz_views.doctorlist,name='doctorlist'),

    url(r'^patientinsert$',yfzz_views.patientinsert,name='patientinsert'),
    url(r'^patientdelete$',yfzz_views.patientdelete,name='patientdelete'),
    url(r'^patientchange$',yfzz_views.patientchange,name='patientchange'),
    url(r'^patientlist',yfzz_views.patientlist,name='patientlist'),

    url(r'^doctorlogin$',yfzz_views.doctorlogin,name='doctorlogin'),
    url(r'^doctorlogout$',yfzz_views.doctorlogout,name='doctorlogout'),
    url(r'^doctorhomepage',yfzz_views.doctorhomepage,name='doctorhomepage'),
    url(r'^dpatientlist',yfzz_views.dpatientlist,name='dpatientlist'),

    url(r'^patientlogin$',yfzz_views.patientlogin,name='patientlogin'),
    url(r'^patientlogout$',yfzz_views.patientlogout,name='patientlogout'),
    url(r'^patienthomepage',yfzz_views.patienthomepage,name='patienthomepage'),

    url(r'^change$',yfzz_views.change,name='change'),
    url(r'^changeoutdeny$',yfzz_views.changeoutdeny,name='changeoutdeny'),
    url(r'^changeindeny$',yfzz_views.changeindeny,name='changeindeny'),


    url(r'^admin/', admin.site.urls),
]
