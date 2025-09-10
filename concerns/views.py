
from django.utils import timezone  
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from user.models import MyUser
from django.db.models import Count
from .models import  Concern
from django.views.generic import View
from article.models import Article
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.



from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.models import MyUser
from article.models import Article
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
logger = logging.getLogger(__name__)


#关注，取消关注API
@login_required
@require_POST
def toggle_concern(request,concerned_user_id):
    # concerns_user_id=request.POST.get('concerns_user_id')
    logger.info(f"[BACKEND] toggle_concern called for user_id: {concerned_user_id}")
    logger.info(f"[BACKEND] Current user: {request.user.id}")
    concerns_user=get_object_or_404(MyUser,id=concerned_user_id)
    current_user=request.user
    #不能关注自己
    if current_user.id==concerns_user.id:
        logger.warning("[BACKEND] User tried to concern themselves")
        return JsonResponse({'status':'error','message':'不能关注自己'})
    
  # 检查是否已经关注
    try:
        concern = Concern.objects.get(user=current_user, concern_user=concerns_user)
        logger.info("[BACKEND] Concern exists, deleting...")
        concern.delete()
        action = 'unconcern'
    except Concern.DoesNotExist:
        logger.info("[BACKEND] Concern does not exist, creating...")
        concern = Concern.objects.create(
            user=current_user,
            concern_user=concerns_user,
            created_at=timezone.now()
        )
        action = 'concern'
    
    logger.info(f"[BACKEND] Action: {action}")
    
    # 发送WebSocket通知
    try:
        channel_layer = get_channel_layer()
        logger.info(f"[BACKEND] Sending WS to user_{concerns_user.id} - Action: {action}")
        async_to_sync(channel_layer.group_send)(
            f'user_{concerns_user.id}',
            {
                "type": "concern_update",
                "action": action,
                "user_id": current_user.id
            }
        )
        
        logger.info(f"[BACKEND] Sending WS to user_{current_user.id} - Action: {action}")
        async_to_sync(channel_layer.group_send)(
            f'user_{current_user.id}',  # 操作者自己的组
            {
                "type": "concern_update",
                "action": action,
                "user_id": concerns_user.id
            }
        )
    except Exception as e:
        logger.error(f"[BACKEND] WebSocket error: {str(e)}")
    
    return JsonResponse({
        'action': action,
        'user_id': current_user.id,         
        'target_id': concerns_user.id
    })

# @login_required
# @require_POST
# def concernuser(request,concern_id,user_id):
#     '''
#     搜索页关注用户
#     '''
#     concerns_user=get_object_or_404(MyUser,id=concern_id)
#     current_user=request.user
#     #不能关注自己
#     if current_user.id==concerns_user.id:
#         return JsonResponse({'status':'error','message':'不能关注自己'})
    



class CheckConcernStatus(APIView):
    def get(self,request,user_id):
        concerns_user=get_object_or_404(MyUser,id=user_id)
        user=request.user
        is_concerned=Concern.objects.filter(user=request.user,concern_user=concerns_user).exists()
        return Response({'is_concerned':is_concerned})


#4. 创建关注者动态流视图
class FeedView(APIView):
    def get(self,request):
        user=request.user
        page=request.GET.get('page',1)
        per_page=10
        
        #获取关注用户的ID列表
        concern_ids=Concern.objects.filter(user=user).values_list('concern_user_id',flat=True)
        ##flat=True：​关键参数，表示将查询结果展平为单一值的列表​（而非元组的列表）。因为这里只查询了一个字段（concern_user_id），
        # 所以flat=True会将结果直接转为[id1, id2, id3, ...]的形式，而不是[(id1,), (id2,), (id3,), ...]（默认返回元组列表）。
        
        
        # 获取当前用户和关注用户的文章
        # 使用annotate优化查询，避免N+1问题
        articles = Article.objects.filter(
            Q(author_id=user.id) | Q(author_id__in=concern_ids)
        ).select_related('author').annotate(comment_count=Count('comment')).order_by('-create_time')
        #使用select_related('author')后，Django会在初始查询中通过
        # SQL JOIN操作一次性获取文章及其作者的信息，减少数据库查询次数，提升性能。
        
        #分页
        paginator=Paginator(articles,per_page)
        page_obj=paginator.get_page(page)
        
        # 序列化数据
        data = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'results': [
                {
                    'id': article.id,
                    'title': article.title,
                    'content': article.content[:100] + '...' if len(article.content) > 100 else article.content,
                    'author': {
                        'id': article.author.id,
                        'username': article.author.username,
                        'avatar': article.author.avatar.url if article.author.avatar else None
                    },
                    'create_time': article.create_time.strftime('%Y-%m-%d %H:%M'),
                    'comment_count': article.comment_count 
                }
                for article in page_obj
            ]
        }
        
        return Response(data)
        
        


























from django.core.paginator import Paginator
@login_required(login_url='tologinpage') 
def concerns(request, id,page):
    '''
    关注列表
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    user = MyUser.objects.filter(id=id).first()  # 获取当前用户
    concern_list = Concern.objects.filter(user=user).order_by('-created_at')  # 获取用户关注的所有用户
    paginator = Paginator(concern_list, 10)  # 每页显示 10 条数据
    try:
        concern2 = paginator.page(page)
    except PageNotAnInteger:
        concern2 = paginator.page(1)
    except EmptyPage:
        concern2 = paginator.page(paginator.num_pages) 
    
    return render(request, 'concerns.html', {'concern2': concern2, 'id': id,'page':page})  # 渲染模板，传入关注列表和当前用户 ID


class UserSearchView(View):
    def get(self, request, id, page):
        """
        处理get请求，显示搜索用户页面
        """
        keyword=request.GET.get('uservalue', '')
        return self._render_search(request, id, page, keyword)
    
    def post(self, request, id, page):
        """
        处理post请求，执行用户搜索
        """
        keyword=request.POST.get('uservalue', '')
        print(f"[BACKEND] Search keyword: {keyword}")
        #POST后重定向到GET，避免表单重复提交
        return redirect(f"{reverse('searchuser', args=[id, page])}?uservalue={keyword}")
    
    def _render_search(self, request, id, page, keyword):
        """
        内部方法，渲染搜索结果页面（get和post共用）
        """
        # user=MyUser.objects.filter(id=id).first()
        user = get_object_or_404(MyUser, id=id)
        print(f"[BACKEND] 查找人ID： {id} 关键词：{keyword}")
        #构建查询集
        queryset = MyUser.objects.all()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(wx__icontains=keyword)
            ).order_by('-id')
        else:
            queryset = MyUser.objects.none()
        
        paginator=Paginator(queryset,10)
        try:
            page_obj=paginator.page(page)
        except PageNotAnInteger:
            page_obj=paginator.page(1)
        except EmptyPage:
            page_obj=paginator.page(paginator.num_pages)
        
        return render(request, 'searchuser.html', {
            'userlist': page_obj,
            'namevalue': keyword,
            'id': user.id,
            'searchuser2': page_obj,
            'page': page
        })