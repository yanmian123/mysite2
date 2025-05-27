from django.urls import re_path
from .views import ImgcodeView 
urlpatterns = [
    re_path('^imgcodes/(?P<uuid>[\w-]+)/$', ImgcodeView.as_view(), name='img_code'),
]
