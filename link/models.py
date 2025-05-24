from django.db import models
from user.models import MyUser
# Create your models here.
class LinkInfo(models.Model):
    '''
    友情链接
    '''
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,verbose_name='链接名称')
    url=models.CharField(max_length=200,verbose_name='链接地址')
    remark=models.CharField(max_length=200,verbose_name='备注',null=True,blank=True)
    user=models.ForeignKey(MyUser,verbose_name='用户',on_delete=models.CASCADE)

    class Meta:
        verbose_name = '友情链接管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name