
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from user.models import MyUser
from .models import  Myconcerns
# Create your views here.

from django.core.paginator import Paginator

def concerns(request, id,page):
    '''
    关注列表
    '''
    user = MyUser.objects.filter(id=id).first()  # 获取当前用户
    concern_list = Myconcerns.objects.filter(user=user).order_by('-create_time')  # 获取用户关注的所有用户
    paginator = Paginator(concern_list, 10)  # 每页显示 10 条数据
    try:
        concern2 = paginator.page(page)
    except PageNotAnInteger:
        concern2 = paginator.page(1)
    except EmptyPage:
        concern2 = paginator.page(paginator.num_pages)
    
    return render(request, 'concerns.html', {'concern2': concern2, 'id': id,'page':page})  # 渲染模板，传入关注列表和当前用户 ID

from django.db.models import Q
def searchuser(request,id,page):
    '''
    搜索用户
    :param request:
    :return:
    '''
    user=MyUser.objects.filter(id=id).first()
    
    keyword=request.POST.get('uservalue') or request.GET.get('uservalue')# 获取搜索关键字
    if keyword:
        userlist = MyUser.objects.filter(
            Q(name__icontains=keyword) | Q(wx__icontains=keyword)
        ).order_by('-id')
    else:
        userlist=MyUser.objects.none() # 如果没有关键字，返回空查询集
        

    paginator = Paginator(userlist, 10)  # 每页显示 10 条数据
    try:
        searchuser2 = paginator.page(page)
    except PageNotAnInteger:
        searchuser2 = paginator.page(1)
    except EmptyPage:
        searchuser2 = paginator.page(paginator.num_pages)
    
    context = {
        'userlist': userlist,
        'namevalue': keyword,  # 传递搜索关键字
        'id': user.id,
        'searchuser2': searchuser2,
        'page': page
    }
    return render(request,'searchuser.html',context)  # 渲染模板，传入搜索结果和当前用户 ID