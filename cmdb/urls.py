"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
import xadmin
from captcha.views import captcha_refresh
from django.conf.urls import include
from django.urls import path

from device.views import AssetAdd, LoginView, LogoutView, index, AnsibleViewPublic, ajax_val, AssetListView, \
    AssetFuncsView, shop_download, decryption, migrate_data, TaskView

urlpatterns = [
    path('mgmt/', xadmin.site.urls),
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('deploy_public/', AnsibleViewPublic.as_view(), name='deploy_public'),
    path('captcha/', include('captcha.urls')),
    path('ajax_val/', ajax_val, name='ajax_val'),
    path('refresh/', captcha_refresh, name='captcha-refresh'),
    path('asset_list/', AssetListView.as_view(), name='assetlist'),
    path('asset_add/', AssetAdd.as_view(), name='assetadd'),
    path('asset_detail/<int:asset_id>/', AssetFuncsView.as_view(), name='assetdetail'),
    path('deploy/', AssetFuncsView.as_view(), name='deploy'),
    path('asset_delete/', AssetFuncsView.as_view(), name='assetdelete'),
    path('asset_update/', AssetFuncsView.as_view(), name='assetupdate'),
    path('shop/', shop_download, name='shop_download'),
    path('domain/', include('domain.urls')),
    path('webssh/', include('webssh.urls')),
    # path('md/', migrate_data),
    path('decryption/', decryption, name='decryption'),
    path('task/', TaskView.as_view(), name='taskview')
]
