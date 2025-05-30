from django.urls import re_path
from .views import ImgcodeView,Textmessage
urlpatterns = [
    re_path('^imgcodes/(?P<uuid>[\w-]+)/$', ImgcodeView.as_view(), name='img_code'),
    re_path('^phonecodes/(?P<phone>1\d{9})/$',Textmessage.as_view(),name='phone_code')
]
