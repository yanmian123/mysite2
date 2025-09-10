# concerns/models.py
from django.db import models
from user.models import MyUser

class Concern(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='concerned_by')
    concern_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='concerned_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'concern_user')
        verbose_name = '关注关系'
        verbose_name_plural = '关注关系'
        
    def __str__(self):
        return f"{self.user.username} 关注 {self.concern_user.username}"