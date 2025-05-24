from django.urls import path
from django.views.generic.base import RedirectView
from article.views import article, articledetail, commentdelete,create_article,search_view,commentreply
urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    path("", RedirectView.as_view(url="user/login.html")),
    path("<int:id>/<int:page>/<int:typeId>.html", article, name="article"),  # 帖子
    path("articledetail/<int:id>/<int:aid>.html", articledetail, name="articledetail"), # 帖子详情
    path('commentdelete/<int:comment_id>/', commentdelete, name='commentdelete'),
    path('create/', create_article, name='article_create'), # 创建文章
    path('search/<int:id>/<int:page>.html', search_view, name='search'),
    path('commentreply/<int:comment_id>/<int:aid>.html', commentreply, name='commentreply'), # 追评
]
