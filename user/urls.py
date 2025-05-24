from django.urls import path
from .views import tologinpage, toregisterpage,register,login,about# Import the required views


urlpatterns = [
    path("login.html", tologinpage,name='tologinpage'),#login.html是路径
    path("register.html", toregisterpage,name='toregisterpage'),
    path("register", register,name='register'), # 注册页面
    path("login",login,name='login'),
    path('about/<int:id>.html', about, name='about'),

]