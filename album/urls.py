from django.urls import path
from album.views import album

urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    # path("base2.html", albumshow, name='albumshow'),  # 相册展示
    path("<int:id>/<int:page>.html",  album, name='album'),  # 帖子
]