from django.urls import path
from .views import concerns, searchuser,concernspersonhome,concernuser # Import the required views

urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    # path("base2.html", albumshow, name='albumshow'),  # 相册展示
    path("<int:id>/<int:page>.html",  concerns, name='concerns'),  # 帖子a
    path("searchuser/<int:id>/<int:page>.html",  searchuser, name='searchuser'),  # 搜索用户
    path('<int:id>/<int:page>/<int:typeId>/concernspersonhome.html',concernspersonhome,name='concernspersonhome'),#被关注的用户的主页详情页面
    # path('concernuser/<int:concern_id>/<int:user_id>/<str:concern_name>/',concernuser,name='concernuser')
    path('concernuser/<int:concern_id>/<int:user_id>/', concernuser, name='concernuser')  # 移除不必要的 concern_name 参数
]