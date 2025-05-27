from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    '''
    自定义用户模型
    '''
    # 这里可以添加其他字段，例如：
    # age = models.IntegerField(null=True, blank=True)
    # phone = models.CharField(max_length=15, null=True, blank=True)
    # 你可以根据需要添加更多字段
    name= models.CharField('姓名',max_length=30, null=True,default='暂无')
    age= models.IntegerField('年龄',null=True, blank=True)
    company = models.CharField('公司',max_length=30, null=True, default='暂无')
    birthday= models.DateField('生日',null=True, blank=True)
    phone = models.CharField('电话',max_length=15, null=True, blank=True)
    address = models.CharField('地址',max_length=100, null=True, default='暂无')
    wx= models.CharField('微信',max_length=30, null=True, default='暂无')
    avatar = models.ImageField('头像',upload_to='avatar/',blank=True, null=True)
    class Meta:
        db_table = 't_Myuser_table'
        verbose_name = '用户表'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name