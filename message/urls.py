from django.urls import path
from message.views import message2

urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    # path("base2.html", albumshow, name='albumshow'),  # 相册展示
    path("<int:id>/<int:page>.html",  message2, name='message2'),  # 帖子a
]