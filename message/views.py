from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import message
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required(login_url='tologinpage') 

def message2(request,id,page):
    '''
    留言信息查询添加
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    pagesize=10 # 每页显示的留言数
    messagelist=message.objects.filter(user_id=id) # 查询所有留言
    paginator=Paginator(messagelist,pagesize) # 分页器
    if request.method=='GET':
        try:
            pageData=paginator.page(page) # 获取当前页的数据
        except PageNotAnInteger:# 如果页码不是整数，返回第一页
            pageData=paginator.page(1)
        except EmptyPage:# 如果页码超过范围，返回最后一页   
            pageData=paginator.page(paginator.num_pages)   
        return render(request, 'message.html',locals())
    else:
        content=request.POST.get('content')
        value={'content':content,'user_id':id}
        message.objects.create(**value) # 创建评论
        kwargs={'id':id,'page':page} # kwargs 是一个字典，用于存储 URL 中的参数
        
        return redirect(reverse('message2',kwargs=kwargs)) # 重定向到帖子详情页 
