from django.urls import path,re_path
from .views import tologinpage, toregisterpage,register,login,about# Import the required views


urlpatterns = [
    path("login.html", tologinpage,name='tologinpage'),#login.html是路径
    re_path("^register/$", toregisterpage,name='toregisterpage'),
    path("register", register,name='register'), 
    re_path("^login/$",login,name='login'),
    path('about/<int:id>.html', about, name='about'),

]