from .models import ArticleType


def getAllArticleType(request):
    """
    获取帖子类型
    """
    return {"articleTypelist": ArticleType.objects.all()}

from .models import MyUser

def about_info(request):
    if request.user.is_authenticated:
        aboutInfo = MyUser.objects.filter(id=request.user.id).first()
        return {'aboutInfo': aboutInfo}
    return {}