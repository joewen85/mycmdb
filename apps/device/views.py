import datetime
import logging
import os
import json

from OpenSSL import crypto
from captcha.models import CaptchaStore
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect, reverse, \
    HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.views import APIView

from device.ansibleapi import AnsibleApi_v2
from device.forms import AddForm, LoginForm, CaptchaForm
from device.models import Envirment, Device, Cloudips, Jobs, Deploy_record
from domain.models import DomainDetail
from .tasks import deploy_task

from django.views.decorators.cache import cache_page
from utils.cryto import RsaCrypto

try:
    from config import Config as CONFIG
except ImportError:
    msg = """

        Error: No config file found.

        You can run `cp config_example.py config.py`, and edit it.
        """
    raise ImportError(msg)

logger = logging.getLogger(__name__)
collect_logger = logging.getLogger('collect')


def ajax_val(request):
    if request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'],
                                         hashkey=request.GET['hashkey'])
        if cs:
            json_data = {'status': 1}
        else:
            json_data = {'status': 0}
        return JsonResponse(json_data)
    else:
        json_data = {'status': 0}
        return JsonResponse(json_data)


def index(request):
    return render(request, "index.html")


class LoginView(View):
    """
    verfy login
    """

    def get(self, request):
        next = request.GET.get('next', '/')
        return render(request, "login.html", {'next': next, 'msg': ""})

    def post(self, request):
        login_form = LoginForm(request.POST)
        next = request.POST.get('next')
        if login_form.is_valid():
            username = request.POST.get('username', "")
            userpassword = request.POST.get('userpassword', "")

            user = auth.authenticate(username=username, password=userpassword)
            if user is not None and user.is_active == 1:
                auth.login(request, user)
                return redirect(next)
            else:
                return render(request, 'login.html',
                              {'msg': '用户名或密码不正确或已被禁用', 'next': next})
        else:
            return render(request, 'login.html',
                          {'login_form': login_form.errors, 'next': next})


class LogoutView(View):
    """
    用户登出
    """

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


@method_decorator(login_required, name='dispatch')
class AssetAdd(View):
    """
    add，modify custom asset
    """

    # @method_decorator(cache_page(60))
    def get(self, request):
        envall = Envirment.objects.all()
        ispall = Cloudips.objects.all()
        return render(request, 'asset.html',
                      {'env_datas': envall, 'cloudisp_datas': ispall})

    def post(self, request):
        if request.method == "POST":
            form = AddForm(request.POST)
            if form.is_valid():
                domain = form.cleaned_data.get('domain')
                ipaddr = form.cleaned_data.get('ipaddress')
                username = request.POST.get('username', None)
                password = request.POST.get('password', None)
                position = form.cleaned_data.get('position')
                envirment = request.POST.get('select1', None)
                cloudips = request.POST.get('select2', None)
                customer_name = request.POST.get('customer_name', None)
                port = form.cleaned_data.get('port')
                others = request.POST.get('others', None)
                shop_version = request.POST.get("shop_ver")
                paid = request.POST.get('vers', 0)
                if Device.objects.filter(hostname=domain).exists():
                    # if get_domain.exists():
                    Device.objects.filter(hostname=domain).update(
                        ipaddress=ipaddr, sshuser=username,
                        sshpassword=password, websitepath=position,
                        envirment_id=envirment, cloudips_id=cloudips,
                        customer_name=customer_name, sshport=port,
                        others=others, paid=paid, shop_version=shop_version,
                        updated_at=datetime.datetime.now())
                    messages.success(request, "域名已存在，已保存其它内容")
                    redirect_url = reverse('assetlist') + '?page=1'
                    return redirect(redirect_url)
                else:
                    encrypt_sshpassword = RsaCrypto().encrypt(password)[
                        'message']
                    device_obj, created = Device.objects.update_or_create(
                        hostname=domain, ipaddress=ipaddr, sshuser=username,
                        websitepath=position, sshport=port, is_maintenance=0,
                        deploy_times=0,
                        cloudips_id=cloudips, envirment_id=envirment,
                        customer_name=customer_name,
                        others=others, paid=paid, shop_version=shop_version)

                    Password_record.objects.create(mysqlpassword='None',
                                                   ftppassword='None',
                                                   sshpassword=encrypt_sshpassword,
                                                   ipaddress=device_obj)
                    try:
                        DomainDetail.objects.update_or_create(domain=domain)
                    except Exception as err:
                        print(err)
                    device_obj, created = Device.objects.update_or_create(
                        hostname=domain, ipaddress=ipaddr,
                        sshuser=username,
                        websitepath=position, sshport=port,
                        is_maintenance=0, deploy_times=0,
                        cloudips_id=cloudips, envirment_id=envirment,
                        customer_name=customer_name,
                        others=others, paid=paid,
                        shop_version=shop_version)

                    Password_record.objects.create(mysqlpassword='None',
                                                   ftppassword='None',
                                                   sshpassword=encrypt_sshpassword,
                                                   ipaddress=device_obj)
                    messages.success(request, "保存资产成功")
                    redirect_url = reverse('assetlist') + '?page=1'
                    return redirect(redirect_url)
            else:
                return render(request, 'asset.html',
                              {'verify_form': form.get_errors()})


@method_decorator(login_required, name='dispatch')
class AssetListView(View):
    """
    list latest 10 asset and search asset
    """

    def get(self, request):
        keyword = request.GET.get('keyword')
        if keyword:
            keyword = str(keyword).strip()
            all_asset_lists = Device.objects.filter(
                Q(customer_name__icontains=keyword) | Q(
                    hostname__icontains=keyword) | Q(
                    ipaddress__icontains=keyword)).order_by('-pk', 'created_at')
        else:
            all_asset_lists = Device.objects.all().order_by('-pk', 'created_at')
        # 分页 每页10条数据
        paginator = Paginator(all_asset_lists, 10)
        # print(paginator.count, paginator.num_pages, paginator.page_range)
        page_range = paginator.page_range
        num_page = paginator.num_pages
        total = paginator.count
        around_count = 2
        leff_has_more = False
        right_has_more = False
        try:
            current_page = int(request.GET.get('page'))
        except Exception as e:
            # messages.success(request, "请勿传入非法值")
            current_page = 1

        try:
            contacts = paginator.get_page(current_page)
        except PageNotAnInteger:
            contacts = paginator.get_page(1)
        except EmptyPage:
            contacts = paginator.get_page(num_page)

        if current_page <= around_count + 2:
            left_range = range(1, current_page)
        else:
            leff_has_more = True
            left_range = range(current_page - around_count, current_page)

        if current_page >= num_page - around_count - 1:
            right_range = range(current_page + 1, num_page + 1)
        else:
            right_has_more = True
            right_range = range(current_page + 1,
                                current_page + around_count + 1)
        return render(request, 'asset_list.html',
                      {'contacts': contacts, 'page_range': page_range,
                       'current_page': current_page,
                       'num_page': num_page, 'left_range': left_range,
                       'right_range': right_range,
                       'left_has_more': leff_has_more,
                       'right_has_more': right_has_more, 'total': total,
                       'msg': '',
                       'keyword': keyword})


@method_decorator(login_required, name='dispatch')
class AssetFuncsView(View):
    """
    asset all functions
    """

    def get(self, request, asset_id):
        if request.method == "GET":
            asset_detail = Device.objects.get(pk=asset_id)
            try:
                password_dict = list(asset_detail.PASSWORD.all().values())[0]
            except Exception as err:
                print(err)
                password_dict = {
                    'sshpassword': 'None',
                    'ftppassword': 'None',
                    'mysqlpassword': 'None',
                    'mongodbpassword': 'None'
                }
            task_list = Jobs.objects.all()
            env_list = Envirment.objects.all()
            isp_list = Cloudips.objects.all()
            deployrec_list = Deploy_record.objects.filter(hostname=asset_id)
            # return JsonResponse({'code': 200, 'message': asset_id, 'data': asset_detail})
            return render(request, 'asset_detail.html',
                          {'asset_detail': asset_detail,
                           'password_records': password_dict,
                           'task_list': task_list,
                           'env_lists': env_list,
                           'cloudisp_list': isp_list,
                           'deploy_records': deployrec_list})

    def post(self, request, asset_id):
        domain = request.POST.get('domain', None)
        ipaddr = request.POST.get('ipaddress', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        position = request.POST.get('position', None)
        ftpuser = request.POST.get('ftpuser', None)
        ftppassword = request.POST.get('ftppassword', None)
        mysqladdress = request.POST.get('mysqladdress', None)
        mysqluser = request.POST.get('mysqluser', None)
        mysqlpassword = request.POST.get('mysqlpassword', None)
        envirment = request.POST.get('select_env', None)
        # envirment = request.POST.get('env', None)
        cloudips = request.POST.get('select_isp', None)
        # cloudips = request.POST.get('cloudips', None)
        customer_name = request.POST.get('customer_name', None)
        port = request.POST.get('port', None)
        job = request.POST.get('select1', None)
        others = request.POST.get('others', None)
        deploy_desc = request.POST.get('desc')
        mongodbuser = request.POST.get('mongodbuser')
        mongodbpassword = request.POST.get('mongodbpassword', None)
        mongodbaddress = request.POST.get('mongodbaddress')
        subdomain = request.POST.get('subdomain', None)
        paid = bool(request.POST.get('vers'))
        cert_file = request.FILES.get('cert')
        private_key = request.FILES.get('privatekey')
        state = request.POST.get('state', None)
        backendip = request.POST.get('backendip', '127.0.0.1')
        # get ssl cert and key

        job_obj = Jobs.objects.get(pk=job)
        try:
            cert_var = cert_file.read().decode('utf8')
            privatekey_var = private_key.read().decode('utf8')
            if job_obj.name != "esign":
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_var)
                sb = cert.get_subject()

                if sb.CN != domain:
                    return render(request, "deploy_result.html",
                                  {"error": "提供证书不正确！您提供的证书为：%s" % sb.CN})
        except Exception as e:
            print(e)
            cert_var = None
            privatekey_var = None

        if paid:
            download_vers = 'paid'
        else:
            download_vers = 'free'
        shop_version = request.POST.get("shop_ver")
        # print("商城版本: {}".format(shop_version))

        # 判断是否盗版
        try:
            if DomainDetail.objects.get(domain=domain).is_blacklist:
                return render(request, 'pirate.html', {'domain': domain})
        except Exception as err:
            print(err)
        try:
            device_obj = Device.objects.get(id=asset_id)
            encrypt_passwords = list(device_obj.PASSWORD.values())[0]
            decrypt_sshpassword = RsaCrypto().decrypt(
                encrypt_passwords['sshpassword']).get('message')
            decrypt_ftppassword = RsaCrypto().decrypt(
                encrypt_passwords['ftppassword']).get('message')
            decrypt_mysqlpassword = RsaCrypto().decrypt(
                encrypt_passwords['mysqlpassword']).get('message')
            decrypt_mongodbpassword = RsaCrypto().decrypt(
                encrypt_passwords['mongodbpassword']).get('message')
        except Exception as err:
            print(err)
            decrypt_ftppassword = 'None'
            decrypt_mysqlpassword = 'None'
            decrypt_mongodbpassword = 'None'

        operator = request.POST.get('user')
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            remote_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            remote_ip = request.META['REMOTE_ADDR']

        print(f"remote_ip: {remote_ip}")

        # operator_id = User.objects.get(username=operator).id

        if 'assetdelete' in request.POST:
            """删除资产"""
            # Device.objects.get(pk=asset_id).delete()
            device_obj.delete()
            messages.success(request, "删除资产成功")
            redirect_url = reverse('assetlist') + '?page=1'
            return redirect(redirect_url)
        elif 'deploy' in request.POST:
            """接收post data，传入ansibleapi核心类，部署各个任务"""
            # 获取envname
            env_name = device_obj.envirment.envname
            cloudips_name = device_obj.cloudips.cloudipsname

            start_time = datetime.datetime.strftime(datetime.datetime.now(),
                                                    '%Y-%m-%d %H:%M:%S')

            # 获取任务路径
            job_path = job_obj.path
            job_name = job_obj.name

            # 判断pc端任务状态传入参数
            if job_name == 'pcpage' and state is None:
                return render(request, "deploy_result.html",
                              {"error": "缺状态参数!"})

            # 获取php环境路径
            phpbin = device_obj.envirment.phpbin
            vhost_path = device_obj.envirment.vhost_path
            fastcgi_pass = device_obj.envirment.fastcgi_pass

            # get operator
            operator = self.request.user.username

            # 执行ansible playbook
            # task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
            result = deploy_task.delay(playbook_path=[job_path],
                                       domain=device_obj.hostname,
                                       ansible_ssh_host=device_obj.ipaddress,
                                       group=env_name, port=device_obj.sshport,
                                       ansible_ssh_user=device_obj.sshuser,
                                       ansible_ssh_pass=decrypt_sshpassword,
                                       phpbin=phpbin,
                                       webpath=device_obj.websitepath,
                                       download_vers=download_vers,
                                       mysql_user=device_obj.mysqluser,
                                       mysql_password=decrypt_mysqlpassword,
                                       mysql_address=device_obj.mysqladdress,
                                       shop_version=shop_version,
                                       vhost_path=vhost_path,
                                       mongodbuser=device_obj.mongodbuser,
                                       mongodbpassword=decrypt_mongodbpassword,
                                       mongodbaddress=device_obj.mongodbaddress,
                                       subdomain=subdomain, cert_var=cert_var,
                                       privatekey_var=privatekey_var,
                                       asset_id=asset_id, isp=cloudips_name,
                                       deploy_desc=deploy_desc,
                                       remote_ip=remote_ip, operator=operator,
                                       start_time=start_time, state=state,
                                       job_name=job_name,
                                       fastcgi_pass=fastcgi_pass,
                                       backendip=backendip)

            print('task_id: %s' % result.task_id)
            print('task_state: %s' % result.state)
            print('task_result: %s' % result.result)

            ret = {
                "code": 0,
                "result": "%s 任务已提交到后台队列....3s后返回" % job_name,
                "next_url": "/asset_detail/%s/" % asset_id
            }
            return render(request, 'jump.html', {"ret": ret})
        else:
            """修改资产"""

            if 'assetupdate' in request.POST:
                encrypt_sshpassword = RsaCrypto().encrypt(password)['message']
                encrypt_ftppassword = RsaCrypto().encrypt(ftppassword)[
                    'message']
                encrypt_mysqlpassword = RsaCrypto().encrypt(mysqlpassword)[
                    'message']
                encrypt_mongodbpassword = RsaCrypto().encrypt(mongodbpassword)[
                    'message']

                try:
                    Device.objects.filter(id=asset_id).update(ipaddress=ipaddr,
                                                              hostname=domain,
                                                              sshuser=username,
                                                              websitepath=position,
                                                              envirment_id=envirment,
                                                              cloudips_id=cloudips,
                                                              customer_name=customer_name,
                                                              sshport=port,
                                                              others=others,
                                                              paid=paid,
                                                              updated_at=datetime.datetime.now(),
                                                              ftpuser=ftpuser,
                                                              mysqladdress=mysqladdress,
                                                              mysqluser=mysqluser,
                                                              shop_version=shop_version,
                                                              mongodbaddress=mongodbaddress,
                                                              mongodbuser=mongodbuser)
                    Password_record.objects.filter(ipaddress=asset_id).update(
                        sshpassword=encrypt_sshpassword,
                        ftppassword=encrypt_ftppassword,
                        mysqlpassword=encrypt_mysqlpassword,
                        mongodbpassword=encrypt_mongodbpassword)
                    DomainDetail.objects.update_or_create(domain=domain)
                    Password_record.objects.filter(ipaddress=asset_id).update(
                        sshpassword=encrypt_sshpassword,
                        ftppassword=encrypt_ftppassword,
                        mysqlpassword=encrypt_mysqlpassword)
                    messages.success(request, "修改内容成功")
                    return redirect(
                        reverse('assetdetail', kwargs={'asset_id': asset_id}))
                except Exception as err:
                    return HttpResponse("保存失败:{0}".format(err))


class AnsibleViewPublic(View):
    """
    接收post data，传入ansibleapi核心。并将内容入库
    """

    def get(self, request):
        env_datas = Envirment.objects.filter(pk=4)
        cloudips_datas = Cloudips.objects.all()

        # 判断用户是否登陆，登陆显示所有任务，anonymous用户只显示10条
        if request.user.is_authenticated:
            jobs = Jobs.objects.all()
        else:
            jobs = Jobs.objects.filter(Q(pk=7) | Q(pk=8))

        captcha_form = CaptchaForm()
        return render(request, 'deploy_public.html',
                      {'env_datas': env_datas, 'cloudips_datas': cloudips_datas,
                       'jobs': jobs,
                       'captcha_form': captcha_form, 'verify_form': {}})

    def post(self, request, *args, **kwargs):
        verify_form = AddForm(request.POST)
        captcha_form = CaptchaForm(request.POST)

        if verify_form.is_valid() and captcha_form.is_valid():
            domain = verify_form.cleaned_data.get('domain')
            ipaddr = verify_form.cleaned_data.get('ipaddress')
            username = verify_form.cleaned_data.get('username')
            password = verify_form.cleaned_data.get('password')
            position = verify_form.cleaned_data.get('position')
            ftpuser = request.POST.get('ftpuser', None)
            ftppassword = request.POST.get('ftppassword', None)
            mysqladdress = request.POST.get('mysqladdress', '127.0.0.1')
            mysqluser = request.POST.get('mysqluser', 'root')
            mysqlpassword = request.POST.get('mysqlpassword', '')
            mongodbaddress = request.POST.get('mongodbaddress', '127.0.0.1')
            mongodbuser = request.POST.get('mongodbuser', 'root')
            mongodbpassword = request.POST.get('mongodbpassword', None)
            envirment = request.POST.get('select1', None)
            cloudips = request.POST.get('select2', None)
            customer_name = verify_form.cleaned_data.get('customer_name')
            port = verify_form.cleaned_data.get('port')
            job = request.POST.get('select3', None)
            others = request.POST.get('others', None)
            deploy_desc = request.POST.get('desc', None)
            # download_vers = request.POST.get('vers', 'free')
            download_vers = 'free'
            shop_version = request.POST.get('shop_ver')
            operator = request.POST.get('user')
            subdomain = request.POST.get('subdomain', None)
            cert_file = request.FILES.get('cert')
            private_key = request.FILES.get('privatekey')
            backendip = request.POST.get('backendip', None)

            # get ssl cert and key
            try:
                cert_var = cert_file.read().decode('utf8')
                privatekey_var = private_key.read().decode('utf8')
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_var)
                sb = cert.get_subject()

                if sb.CN != domain:
                    return render(request, "deploy_result.html",
                                  {"error": "提供证书不正确！您提供的证书为：%s" % sb.CN})
            except Exception as e:
                print(e)
                cert_var = None
                privatekey_var = None

            # 判断是否盗版
            try:
                if DomainDetail.objects.get(domain=domain).is_blacklist:
                    return render(request, 'pirate.html', {'domain': domain})
            except Exception as e:
                print(e)
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                remote_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                remote_ip = request.META['REMOTE_ADDR']
            # 加密
            encrypt_sshpassword = RsaCrypto().encrypt(password)['message']
            encrypt_ftppassword = RsaCrypto().encrypt(ftppassword)['message']
            encrypt_mysqlpassword = RsaCrypto().encrypt(mysqlpassword)[
                'message']
            encrypt_mongodbpassword = RsaCrypto().encrypt(mongodbpassword)[
                'message']

            # operator_id = User.objects.get(username=operator).id

            # 获取envname
            envresult = Envirment.objects.get(id=envirment)
            env_name = envresult.envname

            # 获取任务路径
            job_obj = Jobs.objects.get(pk=job)
            jobpath = job_obj.path
            jobname = job_obj.name
            # print(jobinfo)

            # 获取php环境路径
            phpbin = envresult.phpbin
            vhost_path = envresult.vhost_path

            data = {
                'hostname': domain, 'ipaddress': ipaddr, 'sshuser': username,
                'websitepath': position,
                'envirment_id': envirment, 'cloudips_id': cloudips,
                'customer_name': customer_name, 'sshport': port,
                'others': others, 'mysqluser': mysqluser,
                'mysqladdress': mysqladdress, "shop_version": shop_version,
                "mongodbaddress": mongodbaddress, "mongodbuser": mongodbuser
            }
            custom_asset, created = Device.objects.update_or_create(hostname=domain, defaults=data)
            # 公共部署判断服务器是否部署多次
            # asset_objs = Device.objects.filter(ipaddress=ipaddr)
            # if len(asset_objs) > 3:
            #     messages.error(request, '服务器不能部署太多站点。！')
            #     return redirect(reverse('deploy_public'))
            # # 判断数据库中是否有记录，没有则创建，有则修改
            # created = ''
            # try:
            #     custom_asset, created = Device.objects.update_or_create(
            #         hostname=domain, defaults=data)
            #     custom_asset.PASSWORD.update_or_create(
            #         ipaddress=custom_asset.pk, sshpassword=encrypt_sshpassword,
            #         ftppassword=encrypt_ftppassword,
            #         mysqlpassword=encrypt_mysqlpassword,
            #         mongodbpassword=encrypt_mongodbpassword)
            #     DomainDetail.objects.update_or_create(domain=domain)
            #     custom_asset.PASSWORD.update_or_create(
            #         ipaddress=custom_asset.pk, sshpassword=encrypt_sshpassword,
            #         ftppassword=encrypt_ftppassword,
            #         mysqlpassword=encrypt_mysqlpassword)
            # except Exception as e:
            #     print("数据异常！请联系管理员")
            #
            # if created:
            #     times = custom_asset.deploy_times
            #     weiqingshop_times = custom_asset.deploy_weiqingshop_times
            #     frameworkshop_times = custom_asset.deploy_frameworkshop_times
            #
            #     # limit queue and cronjob check
            #     if times > 5:
            #         messages.error(request, '免费部署计划任务和队列次数已用尽请联系管理员。！！！')
            #         return redirect(reverse('deploy_public'))
            #
            #     # limit weiqingshop check
            #     elif weiqingshop_times > 1:
            #         messages.error(request, '免费部署次数已用尽请联系管理员。！！！')
            #         return redirect(reverse('deploy_public'))
            #
            #     # limit frameworkshop check
            #     elif frameworkshop_times > 1:
            #         messages.error(request, '免费部署次数已用尽请联系管理员。！！！')
            #         return redirect(reverse('deploy_public'))

            # 执行ansible playbook
            runningjob = AnsibleApi_v2()
            runningjob.playbookrun(playbook_path=[jobpath], domain=domain,
                                   ansible_ssh_host=ipaddr, group=env_name,
                                   port=port, ansible_ssh_user=username,
                                   ansible_ssh_pass=password, phpbin=phpbin,
                                   webpath=position,
                                   download_vers=download_vers,
                                   mysql_user=mysqluser,
                                   mysql_password=mysqlpassword,
                                   mysql_address=mysqladdress,
                                   shop_version=shop_version,
                                   vhost_path=vhost_path,
                                   mongodbuser=mongodbuser,
                                   mongodbpassword=mongodbpassword,
                                   mongodbaddress=mongodbaddress,
                                   subdomain=subdomain, cert_var=cert_var,
                                   privatekey_var=privatekey_var, state=None)
            data = runningjob.get_playbook_result()

            # 累计部署记录
            # if jobname == '部署队列和计划任务':
            #     Device.objects.filter(hostname=domain).update(
            #         deploy_times=F('deploy_times') + 1)
            # elif jobname == '部署微擎或商城(微擎框架)':
            #     Device.objects.filter(hostname=domain).update(
            #         deploy_weiqingshop_times=F('deploy_weiqingshop_times') + 1)
            # elif jobname == '部署框架商城(芸众框架)':
            #     Device.objects.filter(hostname=domain).update(
            #         deploy_frameworkshop_times=F(
            #             'deploy_frameworkshop_times') + 1)

            # 获取结果
            if data['ok']:
                deploy_result = data['ok'].get('msg')
            elif data['failed']:
                deploy_result = data['failed'].get('stderr')
            elif data['unreachable']:
                deploy_result = data['unreachable'].get('msg')

            if request.user.is_authenticated:
                operator = request.user.username
            else:
                operator = '免费用户'
            #
            # # 添加部署记录
            Deploy_record.objects.create(
                deploy_datetime=datetime.datetime.now(), hostname=custom_asset,
                operator=operator, remote_ip=remote_ip, desc=deploy_desc,
                jobname=jobname, result=deploy_result)
            print(json.dumps(data, indent=4))
            return render(request, "deploy_result.html",
                          {"data": data, "domain": domain})
        else:
            return render(request, "deploy_public.html",
                          {'verify_form': verify_form.get_errors(),
                           'captcha_form': captcha_form.errors,
                           'descript_form': "error"})


@login_required
def shop_download(request):
    ver = request.GET.get('ver')
    user = request.user.username
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        remote_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        remote_ip = request.META['REMOTE_ADDR']
    file_path = '/data/apps/mycmdb/playbooks/roles/shop/files/{}'.format(ver)
    try:
        file_size = os.path.getsize(file_path)
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Encoding'] = 'unicode'
        response['Content-Length'] = '{}'.format(file_size)
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(ver)
        response['X-Accel-Redirect'] = "/protect_files/{}".format(ver)
        msg = " ".join([user, remote_ip, ':download_file with', ver])
        collect_logger.info(msg)
        return response
    except Exception as e:
        msg = " ".join([user, remote_ip, str(e)])
        collect_logger.info(msg)
        return HttpResponse(e)


from .models import Password_record


def migrate_data(request):
    device_objs = Device.objects.all()
    for device_obj in device_objs:
        # old_data = {
        #     'ftppassword': RsaCrypto().encrypt(device_obj.ftppassword)['message'],
        #     'ipaddress': device_obj,
        #     'sshpassword': RsaCrypto().encrypt(device_obj.sshpassword)['message'],
        #     'mysqlpassword': RsaCrypto().encrypt(device_obj.mysqlpassword)['message']
        # }
        # password_queryset = device_obj.PASSWORD.all()
        old_data = {
            'domain': device_obj.hostname,
            'is_blacklist': 0
        }
        # Password_record.objects.create(**old_data)
        DomainDetail.objects.create(**old_data)
    return HttpResponse('ok')


from django.contrib.auth.decorators import permission_required


# @login_required
@permission_required('device.decode_password', login_url='/login/',
                     raise_exception="无权限操作，请联系管理员")
def decryption(request):
    asset_id = request.GET.get('assetid')
    device_obj = Device.objects.get(pk=asset_id)
    password_dict = list(device_obj.PASSWORD.values())[0]
    sshpassword_decrypt = RsaCrypto().decrypt(password_dict['sshpassword'])
    ftppassword_decrypt = RsaCrypto().decrypt(password_dict['ftppassword'])
    mysqlpassword_decrypt = RsaCrypto().decrypt(password_dict['mysqlpassword'])
    mongodbpassword_decrypt = RsaCrypto().decrypt(
        password_dict['mongodbpassword'])
    data = {
        'sshpassword_state': sshpassword_decrypt['state'],
        'ftppassword_state': ftppassword_decrypt['state'],
        'mysqlpassword_state': mysqlpassword_decrypt['state'],
        'mongodbpassword_state': mongodbpassword_decrypt['state'],

        'sshpassword': sshpassword_decrypt['message'],
        'ftppassword': ftppassword_decrypt['message'],
        'mysqlpassword': mysqlpassword_decrypt['message'],
        'mongodbpassword': mongodbpassword_decrypt['message']
    }
    return JsonResponse(data)


class TaskView(APIView):
    """
    任务调用API
    """

    def post(self, request, *args, **kwargs):
        res = {
            "code": 200,
            "msg": "成功",
            "data": {}
        }
        try:
            domain = DomainDetail.objects.get(domain=request.data.get('domain'))
            task = request.data.get('task')

            try:
                jobpath = Jobs.objects.get(name=task).path
            except Exception as e:
                res['code'] = 400
                res['msg'] = '没有该任务'
                return JsonResponse(res)
            device_obj = Device.objects.get(hostname=domain)
            env_name = device_obj.envirment.envname
            encrypt_passwords = list(device_obj.PASSWORD.values())[0]
            decrypt_sshpassword = RsaCrypto().decrypt(
                encrypt_passwords['sshpassword']).get('message')
            decrypt_ftppassword = RsaCrypto().decrypt(
                encrypt_passwords['ftppassword']).get('message')
            decrypt_mysqlpassword = RsaCrypto().decrypt(
                encrypt_passwords['mysqlpassword']).get('message')
            decrypt_mongodbpassword = RsaCrypto().decrypt(
                encrypt_passwords['mongodbpassword']).get('message')
            phpbin = device_obj.envirment.phpbin
            download_vers = device_obj.paid
            if download_vers:
                download_vers = "1"
            if download_vers is False:
                download_vers = "0"
            shop_version = device_obj.shop_version
            if shop_version:
                shop_version = "1"
            if shop_version is False:
                shop_version = "0"
            vhost_path = device_obj.envirment.vhost_path
            mongodbuser = device_obj.mongodbuser
            mongodbaddress = device_obj.mongodbaddress
            subdomain = request.data.get('subdomain')
            backendip = request.data.get('backendip', '127.0.0.1')
            # get ssl cert and key
            # cert_file = None
            # private_key = None
            # try:
            #     cert_var = cert_file.read().decode('utf8')
            #     privatekey_var = private_key.read().decode('utf8')
            #     cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_var)
            #     sb = cert.get_subject()
            #
            #     if sb.CN != domain:
            #         return render(request, "deploy_result.html",
            #                       {"error": "提供证书不正确！您提供的证书为：%s" % sb.CN})
            # except Exception as e:
            #     print(e)
            cert_var = None
            privatekey_var = None
            asset_id = device_obj.id
            cloudips_name = device_obj.cloudips.cloudipsname
            deploy_desc = request.data.get('deploy_desc')
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                remote_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                remote_ip = request.META['REMOTE_ADDR']

            operator = request.data.get('operator', '授权系统')
            start_time = datetime.datetime.strftime(datetime.datetime.now(),
                                                    '%Y-%m-%d %H:%M:%S')
            state = request.data.get('state', None)
            job_name = task

            if task == 'pcpage' and state is None:
                res['code'] = 500
                res['msg'] = '缺状态参数'
                return JsonResponse(res)

            if domain.is_blacklist is True:
                res['code'] = 401
                res['msg'] = '黑名单不能更新'
            else:
                result = deploy_task.delay(playbook_path=[jobpath],
                                           domain=device_obj.hostname,
                                           ansible_ssh_host=device_obj.ipaddress,
                                           group=env_name,
                                           port=device_obj.sshport,
                                           ansible_ssh_user=device_obj.sshuser,
                                           ansible_ssh_pass=decrypt_sshpassword,
                                           phpbin=phpbin,
                                           webpath=device_obj.websitepath,
                                           download_vers=download_vers,
                                           mysql_user=device_obj.mysqluser,
                                           mysql_password=decrypt_mysqlpassword,
                                           mysql_address=device_obj.mysqladdress,
                                           shop_version=shop_version,
                                           vhost_path=vhost_path,
                                           mongodbuser=mongodbuser,
                                           mongodbpassword=decrypt_mongodbpassword,
                                           mongodbaddress=mongodbaddress,
                                           subdomain=subdomain,
                                           cert_var=cert_var,
                                           privatekey_var=privatekey_var,
                                           asset_id=asset_id, isp=cloudips_name,
                                           deploy_desc=deploy_desc,
                                           remote_ip=remote_ip,
                                           operator=operator,
                                           start_time=start_time,
                                           state=state, job_name=job_name,
                                           backendip=backendip)
        except Exception as e:
            res['code'] = 400
            res['msg'] = "域名不存在"
            print(e)
        return JsonResponse(res)
