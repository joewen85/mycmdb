# -*- coding: utf-8 -*-
# @Time    : 2019-08-09 23:01
# @Author  : Joe
# @Site    :
# @File    : serializers.py
# @Software: PyCharm
# @function: xxxxx

from django.core import validators
from rest_framework import serializers
import re
from .models import DomainDetail


class DomainSerializer(serializers.Serializer):
    """
    Domain 序列化类
    """
    domain = serializers.CharField()

    def validate_domain(self, domain):
        if not re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$', domain):
            raise serializers.ValidationError("invalid field")
        return domain


class BlackListSerializer(serializers.ModelSerializer):
    """
    黑名单
    """
    class Meta:
        model = DomainDetail
        fields = "__all__"

    def validate_domain(self, domain):
        if not re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$', domain):
            raise serializers.ValidationError("invalid field")
        return domain
