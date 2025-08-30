
from django.utils import timezone  
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from user.models import MyUser
from .models import  Myconcerns
from article.models import Article
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.core.paginator import Paginator
@login_required(login_url='tologinpage') 
def concerns(request, id,page):
    '''
    关注列表
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
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

def concernspersonhome(request,id,page,typeId):
    user=MyUser.objects.filter(id=id).first()
    pagesize=3 # 每页显示的帖子数
    print(id,page,typeId)
    if typeId==None or typeId==0:
        articlelist=Article.objects.filter(author_id=id).order_by('-create_time') # 查询所有帖子
    else:
        articlelist=Article.objects.filter(author_id=id,type_id=typeId).order_by('-create_time') # 查询指定类型的帖子
    paginator=Paginator(articlelist,pagesize) # 分页器
    try:
        pagedata=paginator.page(page) # 获取当前页的数据
    except PageNotAnInteger:# 如果页码不是整数，返回第一页
        pagedata=paginator.page(1)
    except EmptyPage:# 如果页码超过范围，返回最后一页   
        pagedata=paginator.page(paginator.num_pages)
    return render(request,"concernspersonhome.html",locals())
    
# @login_required(login_url='tologinpage') 
# def concernuser(request,concern_id,user_id,concern_name):
#     '点击关注之后，把关注对象加入到数据库'
#     value={
#         'id':concern_id,
#         'user':user_id,
#         'concern_user':concern_name,
#         'create_time':timezone.now(),
        
#     }
#     Myconcerns.objects.create(**value)############################把关注的对象加入数据库
#     if request.user.id != id:
#         return redirect(reverse('tologinpage'))
#     kwargs={'id':user_id,'page':0}
#     return redirect(reverse('serchuser',kwargs=kwargs))

# @login_required(login_url='tologinpage')
# def concernuser(request, concern_id, user_id):
#     try:
#         user = MyUser.objects.get(id=user_id)
#         concern_user = MyUser.objects.get(id=concern_id)
#         # 检查是否已经关注
#         if not Myconcerns.objects.filter(user=user, concern_user=concern_user).exists():
#             Myconcerns.objects.create(
#                 user=user,
#                 concern_user=concern_user,
#                 create_time=timezone.now()
#             )
#     except MyUser.DoesNotExist:
#         pass
#     kwargs = {'id': user_id, 'page': 1}
#     return redirect(reverse('searchuser', kwargs=kwargs))
from django.views.decorators.csrf import csrf_exempt
@login_required(login_url='tologinpage')
@csrf_exempt
def concernuser(request, concern_id, user_id):
    try:
        user = MyUser.objects.get(id=user_id)
        concern_user = MyUser.objects.get(id=concern_id)

        # 检查是否已经关注
        existing_concern = Myconcerns.objects.filter(user=user, concern_user=concern_user).first()
        if existing_concern:
            # 如果已关注，则取关
            existing_concern.delete()
            return JsonResponse({'success': True, 'action': 'unfollow'})
        else:
            # 如果未关注，则添加关注
            Myconcerns.objects.create(
                user=user,
                concern_user=concern_user,
                create_time=timezone.now()
            )
            return JsonResponse({'success': True, 'action': 'follow'})
    except MyUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})