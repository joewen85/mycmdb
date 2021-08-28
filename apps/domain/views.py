import logging
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from config import Config as CONFIG
from domain.permissions import IsTokenOrReadOnly

from domain.serializers import DomainSerializer, BlackListSerializer
from device.ansibleapi import AnsibleApi_v2

from .models import DomainDetail

logger = logging.getLogger(__name__)
collect_logger = logging.getLogger('collect')

from config import Config as CONFIG


class DomainView(APIView):
    """
    域名部署接口
    """
    def post(self, request, *args, **kwargs):
        """
        :param kwargs: domain

        :return: Json
        """
        ret = {
            'code': 200,
            'msg': None,
            'data': {}
        }
        serializer = DomainSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            clean_domain = dict(data)
            runningjob = AnsibleApi_v2()
            # run ansible deploy
            runningjob.playbookrun(playbook_path=[CONFIG.PLAYBOOKPATH + "/roles/application_domain/app_doamin.yml"],
                                   domain=clean_domain['domain'], ansible_ssh_host=CONFIG.API_HOSTIP, group=CONFIG.API_GROUP,
                                   port=22, ansible_ssh_user=CONFIG.API_SSHUSER, ansible_ssh_pass=CONFIG.API_SSHPASSWORD, phpbin='/usr/local/php/bin/php',
                                   webpath=CONFIG.API_WEBPATH, download_vers=1, mysql_user="none",
                                   mysql_password="none", mysql_address="none", shop_version=0, vhost_path="none")
            playbook_result = runningjob.get_playbook_result()

            if playbook_result['ok'] and not playbook_result['failed'] and not playbook_result['unreachable']:
                ret['code'] = status.HTTP_200_OK
                ret['msg'] = ' '.join([clean_domain['domain'], 'deploy ok'])
                ret['data'] = serializer.data
            elif playbook_result['failed']:
                ret['code'] = status.HTTP_400_BAD_REQUEST
                ret['msg'] = playbook_result['failed']['msg']
                ret['data'] = clean_domain
            elif playbook_result['unreachable']:
                ret['code'] = status.HTTP_503_SERVICE_UNAVAILABLE
                ret['msg'] = playbook_result['unreachable']['msg']
                ret['data'] = clean_domain
        else:
            ret['code'] = status.HTTP_400_BAD_REQUEST
            ret['msg'] = serializer.errors.get('domain')[0]
            ret['data'] = {}

        msg = ' '.join(['code:%s' % str(ret['code']), 'Msg:%s' % ret['msg']])
        collect_logger.info(msg)

        return JsonResponse(ret)


class BlackListList(generics.ListCreateAPIView):
    """
    blacklist list and create
    """
    queryset = DomainDetail.objects.all()
    serializer_class = BlackListSerializer
    permission_classes = (IsTokenOrReadOnly,)

    def get_queryset(self):
        domain = self.request.GET.get('domain')
        if domain:
            return DomainDetail.objects.filter(domain=domain)
        else:
            return DomainDetail.objects.all()


class BlackListDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DomainDetail.objects.all()
    serializer_class = BlackListSerializer
    permission_classes = (IsTokenOrReadOnly,)
