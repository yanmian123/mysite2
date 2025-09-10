from django.urls import path
from .views import concerns,toggle_concern # Import the required views
from . import views
urlpatterns = [
    # path("test", TestView.as_view(),name='test'),#测试
    # path("base2.html", albumshow, name='albumshow'),  # 相册展示
    path("<int:id>/<int:page>.html",  concerns, name='concerns'),  # 帖子a
    path("searchuser/<int:id>/<int:page>.html",  views.UserSearchView.as_view(), name='searchuser'),  # 搜索用户
    # path('<int:id>/<int:page>/<int:typeId>/concernspersonhome.html',concernspersonhome,name='concernspersonhome'),#被关注的用户的主页详情页面
    # path('concernuser/<int:concern_id>/<int:user_id>/<str:concern_name>/',concernuser,name='concernuser')
    # path('concernuser/<int:concern_id>/<int:user_id>/', concernuser, name='concernuser'),  # 移除不必要的 concern_name 参数
    path('toggle/<int:concerned_user_id>/', toggle_concern, name='toggle_concern'),
    path('check/<int:user_id>/', views.CheckConcernStatus.as_view(), name='check_concern'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('concernuser/<int:concerned_user_id>/', toggle_concern, name='concernuser'),  # 搜索页关注用户
]