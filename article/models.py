from django.db import models
from user.models import MyUser  # Import MyUser
from django.utils import timezone  # Import timezone
from ckeditor.fields import RichTextField

class ArticleType(models.Model):
    """
    博客类别实体
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, verbose_name="标题")
    name = models.CharField(max_length=100, verbose_name="作者")
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="用户")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "博客类别管理"
        verbose_name_plural = "博客类别管理"


# Create your models here.


class Article(models.Model):
    """
    博客帖子实体
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField("标题", max_length=100)
    type = models.ForeignKey(
        ArticleType, on_delete=models.CASCADE, verbose_name="帖子类别"
    )
    content = RichTextField("内容") # 使用RichTextField来支持富文本编辑器
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="用户")
    image = models.ImageField("文章图片", blank=True, upload_to="article/")
    reads = models.IntegerField("阅读量", default=0)
    abstract = models.CharField("摘要", max_length=300)
    create_time = models.DateTimeField("创建时间", default=timezone.now)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    status = models.CharField(max_length=20, default='draft')  # 新增 status 字段
    # 其他字段...


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "博客帖子管理"
        verbose_name_plural = "博客帖子管理"
        
class comment(models.Model):
    """
    博客评论实体
    """

    id = models.AutoField(primary_key=True)
    content = models.TextField("评论内容")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="所属文章")
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name="帖子作者")
    user=models.CharField( verbose_name="评论用户",max_length=60)
    create_time = models.DateTimeField("评论时间", default=timezone.now)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "博客评论管理"
        verbose_name_plural = "博客评论管理"
