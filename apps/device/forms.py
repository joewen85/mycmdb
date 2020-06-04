# -*- coding: utf-8 -*-
# @Time    : 2018/10/20 2:00 PM
# @Author  : Joe
# @Site    :
# @File    : forms.py.py
# @Software: PyCharm
# @function: verify form

from captcha.fields import CaptchaField
from django import forms
from django.core import validators
from .models import Device


class GetError(forms.Form):
    """
    Serialization error message
    """

    def get_errors(self):
        errors = self.errors.get_json_data()
        # print('错误aaaa： %s' % errors)
        all_errors = {}
        for key, message_dicts in errors.items():
            messages = []
            for message_dict in message_dicts:
                messages.append(message_dict['message'])
            all_errors[key] = messages
        return all_errors


class AddForm(GetError):
    customer_name = forms.CharField(required=True, strip=True, error_messages={'required': '不能为空', 'invalid': '格式错误'})
    domain = forms.CharField(validators=[
        validators.RegexValidator(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$',
                                  message='域名格式错误')], strip=True, error_messages={'required': '不能为空'})
    ipaddress = forms.GenericIPAddressField(protocol='both', error_messages={'required': '不能为空', 'invalid': 'IP地址格式错误'},
                                            strip=True)
    port = forms.IntegerField(min_value=1, max_value=65535,
                              error_messages={'required': '不能为空', 'max_value': '请正确填写端口号，1-65535'})
    password = forms.CharField(required=True, error_messages={'required': '不能为空', 'invalid': '格式错误'})
    position = forms.CharField(validators=[validators.RegexValidator(r'^\/\S+', message='路径格式错误')], strip=True,
                               error_messages={'required': '不能为空'})
    username = forms.CharField(required=True, strip=True)

    def clean_ipaddress(self):
        ipaddress = self.cleaned_data.get('ipaddress')
        if ipaddress == '127.0.0.1':
            raise forms.ValidationError(message="填入信息非法")
        return ipaddress

    # def clean_domain(self):
    #     domain = self.cleaned_data.get('domain')
    #     exist = Device.objects.filter(hostname=domain).exists()
    #     if exist:
    #         raise forms.ValidationError(message="%s域名已存在" % domain)
    #     return domain


class LoginForm(forms.Form):
    username = forms.CharField(required=True, strip=True, error_messages={'required': '不能为空', 'invalid': '格式错误'})
    userpassword = forms.CharField(required=True, min_length=3, error_messages={'required': '不能为空', 'invalid': '格式错误'})


class CaptchaForm(forms.Form):
    captcha = CaptchaField(label="验证码")


class DescriptForm(GetError):
    desc = forms.CharField(required=True, min_length=4, error_messages={'required': '不能为空', 'min_length': '认真填写'})
