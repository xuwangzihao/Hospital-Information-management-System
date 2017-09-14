# coding:utf-8
import json
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.db.models import Q

import yfzz.models as index
import hpt.models as hpt

from .forms import LoginForm

import datetime
import pytz

def test(a):
    return HttpResponse(a)

def home(request):
    today=( datetime.date.today())
    #now=datetime.datetime.now()
    #now=now.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
    #now=django.util.timezone.now()
    return render(request, 'home.html',{'today':today})

'-------------------------------admin-----------------------------------------'

def adminhomepage(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    hh=index.Hospital.objects.get(hid=request.session['a_h'])
    #p=hpt.Patient.objects.using(hid).all().get()
    #pid=p.pidtoday
    #return render(request,'adminhomepage.html',{'pid',pid})
    return render(request,'adminhomepage.html',{'hospital':hh.name,
                                                'name':request.session['a_id']
                                                })

def adminlogin(request):
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('a_log', False):
        return HttpResponseRedirect('adminhomepage')

    if request.method == 'POST':# 当提交表单时
        form = LoginForm(request.POST) # form 包含提交的数据
        if form.is_valid():# 如果提交的数据合法

            aid = form.cleaned_data['id']
            password = form.cleaned_data['password']
            try:
                m=index.Myadmin.objects.get(aid=aid)
            except Exception as e :
                return render(request, 'adminlogin.html', {'form': form})
            else:
                h=m.hospital
                hid=h.hid
                if m.password == password:

                    request.session['a_id'] = m.aid
                    request.session['a_log'] = True
                    request.session['a_h']=hid
                    return HttpResponseRedirect('adminhomepage')
                else:
                    return render(request, 'adminlogin.html', {'form': form})
    else:# 当正常访问时
        form = LoginForm()
    return render(request, 'adminlogin.html', {'form': form})
	
def adminlogout(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    try:
        del request.session['a_id']
        del request.session['a_log']
        del request.session['a_h']
    except KeyError:
        pass
    return home(request)

'-------------------------------admin_operation_for_doctor-----------------------------------------'

def doctorinsert(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':

            request.session['opid']=request.POST['id']
            try:
                index.Doctor.objects.get(did=request.session['opid'])
                #hpt.Doctor.objects.using(request.session['a_h']).get(did=request.session['opid'])
            except Exception:
                return render(request, 'doctorchange.html', {'indid': request.session['opid'], 'goback': '/adminhomepage'})
            else:
                dd=index.Doctor.objects.get(did=request.session['opid'])
                del request.session['opid']
                return render(request, 'infopage.html',{'errorinfo':'This id is exist in '+dd.hospital.name+'!','goback':'/adminhomepage'})
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':
            hpt.Doctor.objects.using(request.session['a_h']).create(did=request.POST['id'],
                                                                         password=request.POST['password'],
                                                                         name=request.POST['name'],
                                                                         info=request.POST['info'],
                                                                         )
            hh=index.Hospital.objects.get(hid=request.session['a_h'])
            index.Doctor.objects.create(did=request.POST['id'],
                                        hospital=hh
                                        )
            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'insert doctor successfully!', 'goback': '/adminhomepage'})
        else:
            del request.session['opid']
            return HttpResponseRedirect('doctorinsert')


def doctordelete(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':
            request.session['opid']=request.POST['id']
            try:
                #index.Doctor.objects.get(did=request.session['opid'])
                dd=hpt.Doctor.objects.using(request.session['a_h']).get(did=request.session['opid'])
            except Exception:
                hh = index.Hospital.objects.get(hid=request.session['a_h'])
                del request.session['opid']
                return render(request, 'infopage.html',
                              {'errorinfo': 'This id is not exist in ' + hh.name + '!', 'goback': '/adminhomepage'})
            else:
                return render(request, 'doctorview.html', {'indid': dd.did,
                                                           'inpassword': dd.password,
                                                           'inname': dd.name,
                                                           'ininfo': dd.info,
                                                           'goback': '/adminhomepage',
                                                           })
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':
            d=hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['id'])
            if d.patient_set.count():
                return render(request, 'infopage.html',
                              {'errorinfo': u'医生'+d.did+d.name+u'下属仍有'+d.patient_set.count()+u'个病人'+'<br>'+
                                            u'请先移除该医生下属病人', 'goback': '/adminhomepage'})
            hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['id']).delete()
            index.Doctor.objects.get(did=request.POST['id']).delete()
            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'delete doctor successfully!',
                                                     'goback': '/adminhomepage'})
        else:
            del request.session['opid']
            return HttpResponseRedirect('doctordelete')


def doctorchange(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':
            request.session['opid']=request.POST['id']
            try:
                #index.Doctor.objects.get(did=request.session['opid'])
                dd=hpt.Doctor.objects.using(request.session['a_h']).get(did=request.session['opid'])
            except Exception:
                hh = index.Hospital.objects.get(hid=request.session['a_h'])
                del request.session['opid']
                return render(request, 'infopage.html',
                              {'errorinfo': 'This id is not exist in ' + hh.name + '!', 'goback': '/adminhomepage'})
            else:
                return render(request, 'doctorchange.html', {'indid': dd.did,
                                                           'inpassword': dd.password,
                                                           'inname': dd.name,
                                                           'ininfo': dd.info,
                                                           'goback': '/adminhomepage',
                                                           })
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':
            d = hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['id'])
            d.password = request.POST['password']
            d.name = request.POST['name']
            d.info = request.POST['info']
            d.save()
            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'change doctor\'s information successfully!',
                                                     'goback': '/adminhomepage'})
        else:
            del request.session['opid']
            return HttpResponseRedirect('doctorchange')

def doctorlist(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.method == 'POST':
        d=hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['id'])
        d.password=request.POST['password']
        d.name=request.POST['name']
        d.info = request.POST['info']
        d.save()
        all_d = hpt.Doctor.objects.using(request.session['a_h']).all().values()
        return render(request, 'doctorlist.html', {'doctorlist': all_d})
    else:
        try:
            did=request.GET['did']
        except Exception:
            all_d = hpt.Doctor.objects.using(request.session['a_h']).all().values()
            return render(request, 'doctorlist.html',{'doctorlist':all_d})
        else:
            dd=hpt.Doctor.objects.using(request.session['a_h']).get(did=did)
            #request.GET['did']=None
            return render(request, 'doctorchange.html', {'indid': dd.did,
                                                         'inpassword': dd.password,
                                                         'inname': dd.name,
                                                         'ininfo': dd.info,
                                                         'goback': '/adminhomepage',
                                                         })

'-------------------------------admin_operation_for_patient-----------------------------------------'

def patientinsert(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':

            request.session['opid']=request.POST['id']
            try:
                index.Patient.objects.get(pid=request.session['opid'])
                #hpt.Patient.objects.using(request.session['a_h']).get(pid=request.session['opid'])
            except Exception:
                dl=hpt.Doctor.objects.using(request.session['a_h']).all()
                return render(request, 'patientchange.html', {'inpid': request.session['opid'],
                                                              'doctorlist':dl,
                                                              'goback': '/adminhomepage',
                                                              })
            else:
                pp=index.Patient.objects.get(pid=request.session['opid'])
                del request.session['opid']
                return render(request, 'infopage.html',{'errorinfo':'This id is exist in '+pp.doctor.hospital.name+'!',
                                                        'goback':'/adminhomepage'})
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':
            dd=hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['doctor'])
            p=hpt.Patient.objects.using(request.session['a_h']).create(pid=request.POST['id'],
                                                                         password=request.POST['password'],
                                                                         name=request.POST['name'],
                                                                         info=request.POST['info'],
                                                                         doctor=dd,
                                                                         is_changing=False,
                                                                         )
            d = p.doctor
            d.pcnt += 1
            d.save()
            idd=index.Doctor.objects.get(did=request.POST['doctor'])
            index.Patient.objects.create(pid=request.POST['id'],
                                        doctor=idd,
                                        )
            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'insert patient successfully!',
                                                     'goback': '/adminhomepage'
                                                     })
        else:
            del request.session['opid']
            return HttpResponseRedirect('patientinsert')


def patientdelete(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':
            request.session['opid']=request.POST['id']
            try:
                #index.Patient.objects.get(pid=request.session['opid'])
                pp=hpt.Patient.objects.using(request.session['a_h']).get(pid=request.session['opid'])
            except Exception:
                hh = index.Hospital.objects.get(hid=request.session['a_h'])
                del request.session['opid']
                return render(request, 'infopage.html',
                              {'errorinfo': 'This id is not exist in ' + hh.name + '!', 'goback': '/adminhomepage'})
            else:
                return render(request, 'patientview.html', {'inpid': pp.pid,
                                                           'inpassword': pp.password,
                                                           'inname': pp.name,
                                                           'ininfo': pp.info,
                                                           'indoctor':pp.doctor,
                                                           'goback': '/adminhomepage',
                                                           })
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':

            p=hpt.Patient.objects.using(request.session['a_h']).get(pid=request.POST['id'])
            d=p.doctor
            d.pcnt-=1
            d.save()
            p.delete()
            index.Patient.objects.get(pid=request.POST['id']).delete()

            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'delete patient successfully!', 'goback': '/adminhomepage'})
        else:
            del request.session['opid']
            return HttpResponseRedirect('patientdelete')


def patientchange(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.session.get('opid', '')=='':#没有id
        if request.method == 'POST' and request.POST['id']!='':
            request.session['opid']=request.POST['id']
            try:
                #index.Patient.objects.get(pid=request.session['opid'])
                pp=hpt.Patient.objects.using(request.session['a_h']).get(pid=request.session['opid'])
            except Exception:
                hh = index.Hospital.objects.get(hid=request.session['a_h'])
                del request.session['opid']
                return render(request, 'infopage.html',
                              {'errorinfo': 'This id is not exist in ' + hh.name + '!', 'goback': '/adminhomepage'})
            else:
                dl = hpt.Doctor.objects.using(request.session['a_h']).all()
                return render(request, 'patientchange.html', {'inpid': pp.pid,
                                                           'inpassword': pp.password,
                                                           'inname': pp.name,
                                                           'ininfo': pp.info,
                                                           'doctorlist': dl,
                                                           'defaultdoctor':pp.doctor.did,
                                                           'goback': '/adminhomepage',
                                                           })
        else:
            return render(request, 'numberinput.html')
    else:
        if request.method == 'POST':
            p = hpt.Patient.objects.using(request.session['a_h']).get(pid=request.POST['id'])
            d = p.doctor
            d.pcnt -= 1
            d.save()
            dd = hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['doctor'])

            p.password = request.POST['password']
            p.name = request.POST['name']
            p.info = request.POST['info']
            p.doctor = dd
            p.save()

            d = p.doctor
            d.pcnt += 1
            d.save()
            idd = index.Doctor.objects.get(did=request.POST['doctor'])
            p = index.Patient.objects.get(pid=request.POST['id'])
            p.doctor = idd
            p.save()
            del request.session['opid']
            return render(request, 'infopage.html', {'errorinfo': 'change patient\'s information successfully!',
                                                     'goback': '/adminhomepage'})
        else:
            del request.session['opid']
            return HttpResponseRedirect('patientchange')

def patientlist(request):
    if not request.session.get('a_log', False):
        return HttpResponseRedirect('adminlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.method == 'POST':
        p = hpt.Patient.objects.using(request.session['a_h']).get(pid=request.POST['id'])
        d = p.doctor
        d.pcnt -= 1
        d.save()
        dd = hpt.Doctor.objects.using(request.session['a_h']).get(did=request.POST['doctor'])

        p.password = request.POST['password']
        p.name = request.POST['name']
        p.info = request.POST['info']
        p.doctor=dd
        p.save()

        d = p.doctor
        d.pcnt += 1
        d.save()
        idd = index.Doctor.objects.get(did=request.POST['doctor'])
        p = index.Patient.objects.get(pid=request.POST['id'])
        p.doctor = idd
        p.save()
        all_p = hpt.Patient.objects.using(request.session['a_h']).all().values()
        return render(request, 'patientlist.html', {'patientlist': all_p})
    else:
        try:
            pid=request.GET['pid']
        except Exception:
            all_p = hpt.Patient.objects.using(request.session['a_h']).all().values()
            return render(request, 'patientlist.html',{'patientlist':all_p})
        else:
            pp=hpt.Patient.objects.using(request.session['a_h']).get(pid=pid)
            #request.GET['pid']=None
            dl = hpt.Doctor.objects.using(request.session['a_h']).all()
            return render(request, 'patientchange.html', {'inpid': pp.pid,
                                                          'inpassword': pp.password,
                                                          'inname': pp.name,
                                                          'ininfo': pp.info,
                                                          'doctorlist': dl,
                                                          'defaultdoctor': pp.doctor.did,
                                                          'goback': '/adminhomepage',
                                                          })






'-------------------------------doctor-----------------------------------------'

def doctorhomepage(request):
    #import ipdb
    #ipdb.set_trace()
    if not request.session.get('d_log', False):
        return doctorlogin(request)
    if request.method == 'POST':  # 当提交表单时
        try:
            m = hpt.Message.objects.using(request.session['d_h']).exclude(type='0').exclude(type='2').exclude(
                type='4').exclude(type='5').exclude(type='8').exclude(type='9').filter(
                Q(fromdid=request.session['d_id'])|Q(todid=request.session['d_id'])).get(
                pid=request.session['oppid'])
        except Exception:
            del request.session['oppid']
            return render(request, 'infopage.html', {'errorinfo': u'抱歉，该病人已经从原来医院转出了，您慢了一步',
                                                     'goback': '/doctorlogin'})
        if m.type=='1':
            m.type='0'
            m.save(using=m.fromhid)

            m.type = '4'
            dl=hpt.Doctor.objects.using(m.tohid).all().order_by('pcnt')
            d_list=['0']
            for i in dl:
                d_list.append(i.did)
            m.extra=str(d_list)
            m.save(using=m.tohid)

            m.type = '3'
            m.todid=d_list[1]
            hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                      tohid=m.tohid,
                                                      fromdid=m.fromdid,
                                                      todid=m.todid,
                                                      title=m.title,
                                                      info=m.info,
                                                      type=m.type,
                                                      extra=m.extra,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now()
                                                      )

            m.type = '8'
            m.todid = '0'
            d_list = [1]
            for i in dl:
                d_list.append(0)
            m.extra = str(d_list)
            hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                      tohid=m.tohid,
                                                      fromdid=m.fromdid,
                                                      todid=m.todid,
                                                      title=m.title,
                                                      info=m.info,
                                                      type=m.type,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now(),
                                                      extra=m.extra)
            del request.session['oppid']
            return render(request,'infopage.html',{'errorinfo':u'您已同意该病人的转出申请~',
                                                   'goback':'/doctorlogin'})
        elif m.type=='3':
            'check该病人是否还在原来的医院等待'
            try:
                p=hpt.Patient.objects.using(m.fromhid).get(pid=request.session['oppid'])
            except Exception:
                del request.session['oppid']
                return render(request, 'infopage.html', {'errorinfo': u'抱歉，该病人已经从原来医院转出了，您慢了一步',
                                                         'goback': '/doctorlogin'})
            else:
                '转诊'
                p.delete(using=m.fromhid)
                #p.is_changing=False
                d = p.doctor
                d.pcnt -= 1
                d.save()
                dd = hpt.Doctor.objects.using(request.session['d_h']).get(did=request.session['d_id'])
                #p.doctor = dd
                p=hpt.Patient.objects.using(m.tohid).create(pid=p.pid,
                                                          password=p.password,
                                                          name=p.name,
                                                          info=p.info,
                                                          doctor=dd,
                                                          )
                #p.save(using=m.tohid)
                d = p.doctor
                d.pcnt += 1
                d.save()
                idd = index.Doctor.objects.get(did=request.session['d_id'])
                ipp = index.Patient.objects.get(pid=request.session['oppid'])
                ipp.doctor = idd
                ipp.save()
                '清理老医院message'
                ml=hpt.Message.objects.using(m.fromhid).filter(pid=p.pid)
                for i in ml:
                    i.type='0'
                    i.save()
                '清理新医院message'
                ml = hpt.Message.objects.using(m.tohid).filter(pid=p.pid)
                for i in ml:
                    i.type = '0'
                    i.save()
                '新增成功提醒'
                m.type='6'
                m.title=u'病人'+p.pid+' '+p.name+u'转诊成功！'
                m.info=m.title+u'谢谢您'
                hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                          tohid=m.tohid,
                                                          fromdid=m.fromdid,
                                                          todid=m.todid,
                                                          title=m.title,
                                                          info=m.info,
                                                          type=m.type,
                                                          pid=m.pid,
                                                          pub_time=datetime.datetime.now(),
                                                          extra=m.extra)
                hpt.Message.objects.using(m.fromhid).create(fromhid=m.fromhid,
                                                          tohid=m.tohid,
                                                          fromdid=m.fromdid,
                                                          todid=m.todid,
                                                          title=m.title,
                                                          info=m.info,
                                                          type=m.type,
                                                          pid=m.pid,
                                                          pub_time=datetime.datetime.now(),
                                                          extra=m.extra)
                m.type = '5'
                hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                          tohid=m.tohid,
                                                          fromdid=m.fromdid,
                                                          todid=m.todid,
                                                          title=m.title,
                                                          info=m.info,
                                                          type=m.type,
                                                          pid=m.pid,
                                                          pub_time=datetime.datetime.now(),
                                                          extra=m.extra)
                del request.session['oppid']
                return render(request, 'infopage.html', {'errorinfo': u'您成功接受该病人，谢谢您的努力！',
                                                         'goback': '/doctorlogin'})
    else:
        try:
            pid=request.GET['pid']
        except:
            d = hpt.Doctor.objects.using(request.session['d_h']).get(did=request.session['d_id'])
            h = index.Hospital.objects.get(hid=request.session['d_h'])
            mlist = hpt.Message.objects.using(request.session['d_h']).filter(
                Q(fromdid=request.session['d_id'])|Q(todid=request.session['d_id'])).exclude(
                type='0').exclude(type='2').exclude(type='4').exclude(
                type='5').exclude(type='8').exclude(type='9')
            return render(request, 'doctorhomepage.html', {'hospital': h.name, 'name': d.name, 'mlist': mlist})

        else:
            request.session['oppid']=pid
            try:
                m = hpt.Message.objects.using(request.session['d_h']).exclude(type='0').exclude(type='2').exclude(
                type='4').exclude(type='5').exclude(type='8').exclude(type='9').filter(
                    Q(fromdid=request.session['d_id'])|Q(todid=request.session['d_id'])).get(pid=pid)
            except Exception:
                del request.session['oppid']
                return render(request, 'infopage.html', {'errorinfo': u'抱歉，该病人已经从原来医院转出了，您慢了一步',
                                                         'goback': '/doctorlogin'})
            if m.type == '1':
                return render(request, 'message.html', {'message': m.info,
                                                        'goback': '/changeoutdeny'})
            elif m.type == '3':
                return render(request, 'message.html', {'message': m.info,
                                                        'goback': '/changeindeny'})
            elif m.type == '6':
                m.type = '0'
                m.save()
                return render(request,'infopage.html', {'errorinfo':m.info,
                                                        'goback':'/doctorlogin'})
            elif m.type == '7':
                m.type = '0'
                m.save()
                return render(request, 'infopage.html', {'errorinfo': m.info,
                                                         'goback': '/doctorlogin'})
            else:
                return test('web has been hacked!')

def changeoutdeny(request):
    if not request.session.get('d_log', False):
        return HttpResponseRedirect('doctorlogin')
    if request.method == 'POST':  # 当提交表单时
        pass
    else:
        m = hpt.Message.objects.using(request.session['d_h']).get(pid=request.session['oppid'],type='1')
        m.type = '0'
        m.save(using=m.fromhid)
        m.type = '2'
        m.title=u'您的转诊申请被你的直属医生拒绝了'
        m.info += '<br>' + u'您的转诊申请被你的直属医生拒绝了，详情请与他取得联系得到答案'
        hpt.Message.objects.using(m.fromhid).create(fromhid=m.fromhid,
                                                    tohid=m.tohid,
                                                    fromdid=m.fromdid,
                                                    todid=m.todid,
                                                    title=m.title,
                                                    info=m.info,
                                                    type=m.type,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now(),
                                                    extra=m.extra)
        del request.session['oppid']
        return render(request, 'infopage.html', {'errorinfo': u'您已经拒绝了该病人的转院（出）申请',
                                                'goback': '/doctorhomepage'})

def changeindeny(request):
    if not request.session.get('d_log', False):
        return HttpResponseRedirect('doctorlogin')
    try:
        m = hpt.Message.objects.using(request.session['d_h']).get(pid=request.session['oppid'],type='3')
    except Exception:
        del request.session['oppid']
        return render(request, 'infopage.html', {'errorinfo': u'您已经拒绝该病人的申请',
                                                 'goback': '/doctorhomepage'})

    th=index.Hospital.objects.get(hid=request.session['d_h'])
    p = hpt.Patient.objects.using(m.fromhid).get(pid=request.session['oppid'])
    mh=hpt.Message.objects.using(request.session['d_h']).get(pid=request.session['oppid'],type='4')
    mb=hpt.Message.objects.using(request.session['d_h']).get(pid=request.session['oppid'],type='8')
    dl=eval(mh.extra)
    db=eval(mb.extra)
    x=dl.index(m.todid)
    db[x]=1
    mb.extra=str(db)
    mb.save()
    flag=0
    for i in db:
        if i==0:
            flag=1
            break
    if flag==0:
        m.type='0'
        m.save()
        mh.type = '0'
        mh.save()
        mb.type = '0'
        mb.save()
        m.type = '7'
        m.title = u'病人' + p.pid + ' ' + p.name + u'的转诊申请已经被医院'+th.name+u'所有医生拒绝。。。'
        m.info = m.title + u'谢谢您'
        hpt.Message.objects.using(m.fromhid).create(fromhid=m.fromhid,
                                                    tohid=m.tohid,
                                                    fromdid=m.fromdid,
                                                    todid=m.todid,
                                                    title=m.title,
                                                    info=m.info,
                                                    type=m.type,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now(),
                                                    extra=m.extra)
        m.type = '9'
        hpt.Message.objects.using(m.fromhid).create(fromhid=m.fromhid,
                                                    tohid=m.tohid,
                                                    fromdid=m.fromdid,
                                                    todid=m.todid,
                                                    title=m.title,
                                                    info=m.info,
                                                    type=m.type,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now(),
                                                    extra=m.extra)
    else:
        m.type = '0'
        m.save()
        if x*2<len(db):
            m.type = '3'
            m.todid = dl[x*2]
            hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                      tohid=m.tohid,
                                                      fromdid=m.fromdid,
                                                      todid=m.todid,
                                                      title=m.title,
                                                      info=m.info,
                                                      type=m.type,
                                                      extra=m.extra,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now()
                                                      )
        if x*2+1 < len(db):
            m.type = '3'
            m.todid = dl[x*2+1]
            hpt.Message.objects.using(m.tohid).create(fromhid=m.fromhid,
                                                      tohid=m.tohid,
                                                      fromdid=m.fromdid,
                                                      todid=m.todid,
                                                      title=m.title,
                                                      info=m.info,
                                                      type=m.type,
                                                      extra=m.extra,
                                                      pid=m.pid,
                                                      pub_time=datetime.datetime.now()
                                                      )
    del request.session['oppid']
    return render(request, 'infopage.html', {'errorinfo': u'您已经拒绝该病人的申请',
                                                'goback': '/doctorhomepage'})

def doctorlogin(request):
    if request.session.get('d_log', False):
        try:
            hpt.Doctor.objects.using(request.session['d_h']).get(did=request.session['d_id'])
        except Exception:
            try:
                del request.session['d_id']
                del request.session['d_log']
                del request.session['d_h']
            except KeyError:
                pass
        else:
            return doctorhomepage(request)
    if request.method == 'POST':# 当提交表单时
        form = LoginForm(request.POST) # form 包含提交的数据
        if form.is_valid():# 如果提交的数据合法
            
            did = form.cleaned_data['id']
            password = form.cleaned_data['password']
            try:
                m_index = index.Doctor.objects.get(did=did)
            except Exception as e :
                #return test(str(e))
                render(request, 'doctorlogin.html', {'form': form})
            else:
                h=m_index.hospital
                hid=h.hid
                m=hpt.Doctor.objects.using(hid).get(did=did)
                if m.password == password:
                    request.session['d_id'] = m.did
                    request.session['d_log'] = True
                    request.session['d_h']=hid
                    return HttpResponseRedirect('doctorhomepage')
                else:
                    #return HttpResponse("Your username and password didn't match.")
                    return render(request, 'doctorlogin.html', {'form': form})
    else:# 当正常访问时
        form = LoginForm()
    return render(request, 'doctorlogin.html', {'form': form})
	
def doctorlogout(request):
    if not request.session.get('d_log', False):
        return HttpResponseRedirect('doctorlogin')
    try:
        del request.session['d_id']
        del request.session['d_log']
        del request.session['d_h']
    except KeyError:
        pass
    return home(request)

def dpatientlist(request):
    if not request.session.get('d_log', False):
        return HttpResponseRedirect('doctorlogin')
    #import ipdb
    #ipdb.set_trace()
    if request.method == 'POST':
        hpt.Patient.objects.using(request.session['d_h']).get(pid=request.POST['id']).delete()
        dd = hpt.Doctor.objects.using(request.session['d_h']).get(did=request.POST['doctor'])
        hpt.Patient.objects.using(request.session['d_h']).create(pid=request.POST['id'],
                                                                 password=request.POST['password'],
                                                                 name=request.POST['name'],
                                                                 info=request.POST['info'],
                                                                 doctor=dd,
                                                                 is_changing=False,
                                                                 )
        all_p = hpt.Patient.objects.using(request.session['d_h']).all().values()
        return render(request, 'dpatientlist.html', {'patientlist': all_p})
    else:
        try:
            pid = request.GET['pid']
        except Exception:
            all_p = hpt.Patient.objects.using(request.session['d_h']).all().values()
            return render(request, 'dpatientlist.html', {'patientlist': all_p})
        else:
            pp = hpt.Patient.objects.using(request.session['d_h']).get(pid=pid)
            #request.GET['pid']=None
            dl = hpt.Doctor.objects.using(request.session['d_h']).get(did=request.session['d_id'])
            return render(request, 'dpatientchange.html', {'inpid': pp.pid,
                                                          'inpassword': pp.password,
                                                          'inname': pp.name,
                                                          'ininfo': pp.info,
                                                          'doctorlist': dl,
                                                          'goback': '/doctorhomepage',
                                                           })
'-------------------------------patient-----------------------------------------'

def patienthomepage(request):
    if not request.session.get('p_log', False):
        return HttpResponseRedirect('patientlogin')
    if request.method=='POST':
        pass
    else:
        p = hpt.Patient.objects.using(request.session['p_h']).get(pid=request.session['p_id'])
        try:
            pid = request.GET['pid']
        except:
            h = index.Hospital.objects.get(hid=request.session['p_h'])
            mlist = hpt.Message.objects.using(request.session['p_h']).filter(pid=request.session['p_id']).exclude(
                type='0').exclude(type='1').exclude(type='3').exclude(type='4').exclude(type='7').exclude(
                type='8').exclude(type='6')
            return render(request,'patienthomepage.html',{'hospital': h.name, 'name': p.name, 'mlist': mlist})
        else:
            request.session['oppid'] = pid
            m = hpt.Message.objects.using(request.session['p_h']).exclude(type='0').exclude(type='1').exclude(
                type='3').exclude(type='4').exclude(type='7').exclude(type='8').get(pid=pid)
            if m.type == '2':
                m.type='0'
                m.save()
                p.is_changing=False
                p.save()
                return render(request, 'infopage.html', {'errorinfo': m.info,
                                                        'goback': '/patientlogin'})
            elif m.type == '5':
                m.type = '0'
                m.save()
                return render(request, 'infopage.html', {'errorinfo': m.info,
                                                        'goback': '/patientlogin'})
            elif m.type == '9':
                m.type = '0'
                m.save()
                p.is_changing = False
                p.save()
                return render(request, 'infopage.html', {'errorinfo': m.info,
                                                         'goback': '/patientlogin'})
            else:
                return test('error')


def patientlogin(request):
    if request.session.get('p_log', False):
        try:
            hpt.Patient.objects.using(request.session['p_h']).get(pid=request.session['p_id'])
        except Exception:
            try:
                del request.session['p_id']
                del request.session['p_log']
                del request.session['p_h']
            except KeyError:
                pass
        else:
            return patienthomepage(request)
    if request.method == 'POST':# 当提交表单时
        form = LoginForm(request.POST) # form 包含提交的数据
        if form.is_valid():# 如果提交的数据合法
            
            pid = form.cleaned_data['id']
            password = form.cleaned_data['password']
            try:
                m_index = index.Patient.objects.get(pid=pid)
            except Exception as e :
                #return test(str(e))
                render(request, 'patientlogin.html', {'form': form})
            else:
                h=m_index.doctor.hospital
                hid=h.hid
                m=hpt.Patient.objects.using(hid).get(pid=pid)
                if m.password == password:
                    request.session['p_id'] = m.pid
                    request.session['p_log'] = True
                    request.session['p_h']=hid
                    return HttpResponseRedirect('patienthomepage')
                else:
                    #return HttpResponse("Your username and password didn't match.")
                    return render(request, 'patientlogin.html', {'form': form})
    else:# 当正常访问时
        form = LoginForm()
    return render(request, 'patientlogin.html', {'form': form})
	
def patientlogout(request):
    if not request.session.get('p_log', False):
        return HttpResponseRedirect('patientlogin')
    try:
        del request.session['p_id']
        del request.session['p_log']
        del request.session['p_h']
    except KeyError:
        pass
    return home(request)

def change(request):
    if not request.session.get('p_log', False):
        return HttpResponseRedirect('patientlogin')
    p=hpt.Patient.objects.using(request.session['p_h']).get(pid=request.session['p_id'])
    if p.is_changing:
        return render(request,'infopage.html',{'errorinfo':'you are already in changing state!',
                                               'goback': '/patienthomepage'})
    if request.method == 'POST':
        hpt.Message.objects.using(request.session['p_h']).create(fromhid=request.session['p_h'],
                                   fromdid=p.doctor.did,
                                   tohid=request.POST['hospital'],
                                   todid='0',
                                   pid=p.pid,
                                   title=u'患者'+p.pid+u'想要转诊',
                                   info=u'患者：'+p.pid+u'想要转诊'+"\n<br>\n"+
                                        u'姓名：'+p.name+"\n<br>\n"+
                                        u'信息：'+p.info+"\n<br>\n"+
                                        u'原因：'+request.POST['info']+"\n<br>\n",
                                   pub_time=datetime.datetime.now(),
                                   type='1',
                                   )
        p.is_changing=True
        p.save()
        return render(request, 'infopage.html',
                      {'errorinfo': u'转诊申请提交成功，请耐心等待!',
                       'goback': '/patienthomepage'})
    else:
        h_l=index.Hospital.objects.all()
        return render(request,'change.html',{'h_list':h_l,
                                             'my_h':request.session['p_h'],
                                              'message':u'患者'+p.pid+u'想要转诊'+"\n<br>\n"+
                                                        u'姓名'+p.name+"\n<br>\n"+
                                                        u'信息'+p.info+"\n<br>\n",
                                              'goback':'/patienthomepage'})

'-------------------------------message_system-----------------------------------------'










# Create your views here.
