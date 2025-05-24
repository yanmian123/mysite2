from django.db import models

# Create your models here.
class Myconcerns(models.Model):
    """
    关注实体
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('user.MyUser', on_delete=models.CASCADE, verbose_name="用户")
    concern_user = models.ForeignKey('user.MyUser', on_delete=models.CASCADE, related_name='concerned_user', verbose_name="关注的用户")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")