from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Albuminfo
def album(request,id,page):
    '''
    相册展示
    :param request:
    :return:
    '''
    pagesize=6 # 每页显示的图片数
    albumlist=Albuminfo.objects.filter(user_id=id) # 查询所有图片
    paginator=Paginator(albumlist,pagesize) # 分页器 
    try:
        pageData=paginator.page(page) # 获取当前页的数据
    except PageNotAnInteger:# 如果页码不是整数，返回第一页
        pageData=paginator.page(1)
    except EmptyPage:# 如果页码超过范围，返回最后一页   
        pageData=paginator.page(paginator.num_pages)
    print(pageData.object_list)
    return render(request,'album.html',locals())

# Create your views here.
