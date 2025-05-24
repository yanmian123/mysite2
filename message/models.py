from django.db import models
from django.utils import timezone   
from user.models import MyUser
# Create your models here.
class message(models.Model):
    '''
    留言实体
    '''
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,verbose_name='留言人')
    email=models.EmailField(verbose_name='邮箱')   
    content=models.TextField(verbose_name='留言内容')
    created_time=models.DateTimeField(default=timezone.now,verbose_name='留言时间')
    user=models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='用户', null=True, blank=True)
    

    def __str__(self):
        return self.content
    
    class Meta:
        verbose_name = '留言管理   '
        verbose_name_plural = '留言管理'