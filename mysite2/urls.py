"""
URL configuration for mysite2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.core.asgi import get_asgi_application
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from article import consumers, routing  # 新增导入
from mysite2 import settings
from mysite2 import views  # Replace 'my_app' with the actual app name where views.echo is defined

urlpatterns = [
    path("admin/", admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path("echo/",views.echo),
    # path("message/",include('message.urls')),
    # path("link/",include('link.urls')),
    path("article/",include('article.urls')),
    path("album/",include('album.urls')),
    path("user/",include('user.urls')), 
    path("message/",include('message.urls')),
    path("concerns/", include('concerns.urls')),
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT},name='media'),
    re_path('static/(?P<path>.*)', serve, {'document_root': settings.STATIC_ROOT},name='static'),
    # path("myview/", views.my_view, name="my_view"),  # Add this line to include the view
    # path("verifications/", include('verifications.urls'), name='verifications'),
    # re_path(r'^ws/article/(?P<article_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
]
