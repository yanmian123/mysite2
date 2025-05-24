from django.urls import path
from .views import concerns, searchuser  # Import the required views

urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    # path("base2.html", albumshow, name='albumshow'),  # 相册展示
    path("<int:id>/<int:page>.html",  concerns, name='concerns'),  # 帖子a
    path("searchuser/<int:id>/<int:page>.html",  searchuser, name='searchuser'),  # 搜索用户
]