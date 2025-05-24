from .models import ArticleType


def getAllArticleType(request):
    """
    获取帖子类型
    """
    return {"articleTypelist": ArticleType.objects.all()}
