from django.db import models
from device.models import Device
# Create your models here.


class DomainDetail(models.Model):
    domain = models.CharField(max_length=50, verbose_name="域名", db_index=True, unique=True)
    # 黑名单为1，白名单为0
    is_blacklist = models.BooleanField(verbose_name="是否黑名单", default=0)

    class Meta:
        verbose_name = "域名详情"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.domain
