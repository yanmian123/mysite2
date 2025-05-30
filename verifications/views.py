from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
import string
import random
import uuid
from captcha.image import ImageCaptcha
from django_redis import get_redis_connection#连接redis库
class ImgcodeView(View):
    """
    视图类，用于处理图像验证码的生成和返回
    """
    def get(self, request,uuid):
        # 生成图像验证码的逻辑
        seed=string.digits
        r=random.sample(seed,4)
        code=''.join(r) 
        # 返回生成的图像验证码
        imgcode=ImageCaptcha().generate(chars=code)
        
        #保存验证码图片到redis数据库
        redis_conn=get_redis_connection('verify_code').set(uuid,code,ex=60*5)  # 设置验证码有效期为5分钟
        return HttpResponse(imgcode, content_type='image/png')

class Textmessage(View):
    """
    视图类2，短信验证码的生成和返回
    :param request：请求对象
    param phone手机号
    return JSON数据 
    """
    def get(self,request,phonenumber):
        pass