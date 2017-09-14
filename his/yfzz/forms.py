# coding:utf-8

from django import forms
 
class LoginForm(forms.Form):
    id = forms.CharField(label=(u"用户名"), max_length=254)
    password = forms.CharField(label=(u"密码"), widget=forms.PasswordInput)

