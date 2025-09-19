from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.views import View
from django.utils import timezone
from article.models import ArticleType
from concerns.models import Concern
from .models import Article, MyUser, Comment
from .form import ArticleForm
from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Prefetch, F   
from .utils import view_counter
from .tasks import increment_article_views
# Create your views here.

@login_required(login_url='tologinpage')
def article(request,id,page,typeId):
    '''
    查询帖子信息
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    user=MyUser.objects.filter(id=id).first()
    if user==None:
        return redirect(reverse('toregisterpage'))
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
    return render(request,'article.html',locals())#作用是把当前作用域里的所有局部变量传递给 render 函数
                                                  #。render 函数会将这些变量作为上下文传递给 article.html 模板，这样在模板文件里就能使用这些变量了。
                                                  
                                                  
                                   
class ArticleFeedView(LoginRequiredMixin, ListView):
    """显示当前用户及其关注用户的文章动态（类视图实现）"""
    template_name = 'articlefeed.html'
    context_object_name = 'pagedata'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        # 获取关注用户的ID列表
        concern_ids = Concern.objects.filter(user=user).values_list('concern_user_id', flat=True)
        user_ids = list(concern_ids)
        user_ids.append(user.id)  # 包括当前用户自己
        
        # 优化查询：减少数据库访问次数
        return Article.objects.filter(author_id__in=user_ids) \
            .select_related('author') \
            .prefetch_related(
                Prefetch('comment_set', queryset=Comment.objects.select_related('author'))
            ) \
            .order_by('-create_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        
        # 添加额外上下文（可选）
        context['feed_title'] = "关注动态"
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # 可以在这里添加额外的请求预处理逻辑
        return super().dispatch(request, *args, **kwargs)

from .utils import view_counter
from .tasks import increment_article_views

# @login_required(login_url='tologinpage')                                                 
# def articledetail(request,id,aid):
#     '''
#     查询帖子详情
#     :param request:
#     :param id: 用户id       
#     :param aid: 某个帖子的id
#     '''    
#     if request.user.id != id:
#         return redirect(reverse('tologinpage'))
#     if request.method=='GET':
#         user=MyUser.objects.filter(id=id).first()
#         article=Article.objects.filter(id=aid).first() # 查询帖子
#         # Article.objects.filter(id=aid).update(reads=article.reads+1) # 更新阅读量
#         if article==None:   
#             return HttpResponse("没有该帖子")
        
#         print(f"[DEBUG] Triggered view increment for article {aid} by user {request.user.id}")
#     if article:
#         # 使用F表达式避免竞态条件
#         # Article.objects.filter(id=aid).update(reads=F('reads') + 1)
#         # 异步增加阅读量（使用Celery任务）
#         increment_article_views.delay(aid, request.user.id)
        
        
#         # 获取实时阅读量
#         realtime_views = view_counter.get_views(aid)
#         unique_views = view_counter.get_unique_views(aid)
        
#         articlecomment = Comment.objects.filter(
#             article_id=aid, 
#             parent_comment__isnull=True
#         ).order_by('-create_time')
#         return render(request, 'articledetail.html', {
#             'article': article,
#             'user': user,
#             'articlecomment': articlecomment,
#             'realtime_views': realtime_views,
#             'unique_views': unique_views
#         })
@login_required(login_url='tologinpage')                                                 
def articledetail(request, id, aid):
    '''
    查询帖子详情
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
        
    if request.method == 'GET':
        user = MyUser.objects.filter(id=id).first()
        article = Article.objects.filter(id=aid).first()
        increment_article_views.delay(aid, request.user.id)
        if article is None:
            return HttpResponse("没有该帖子")
        
        # 获取实时阅读量
        realtime_views = view_counter.get_views(aid)
        unique_views = view_counter.get_unique_views(aid)
        
        # 如果Redis中没有数据，使用数据库中的值
        if realtime_views == 0:
            realtime_views = article.reads
        
        articlecomment = Comment.objects.filter(
            article_id=aid, 
            parent_comment__isnull=True
        ).order_by('-create_time')
        
        return render(request, 'articledetail.html', {
            'article': article,
            'user': user,
            'articlecomment': articlecomment,
            'realtime_views': realtime_views,
            'unique_views': unique_views
        })
    

def commentdelete(request, comment_id):
    if request.method == 'POST':
        try:
            comment1 = Comment.objects.get(id=comment_id)
            comment1.delete()
        except Comment.DoesNotExist:
            pass
        kwargs={'id':comment1.author_id,'aid':comment1.article_id}
    return redirect(reverse('articledetail',kwargs=kwargs)) # 重定向到帖子详情页


def commentreply(request, comment_id, aid):
    if request.method == 'POST':
        try:
            comment1 = Comment.objects.get(id=comment_id)
            commentauthor = comment1.author_id
        except Comment.DoesNotExist:
            return HttpResponse("评论不存在")
        content = request.POST.get('content')
        if not content:
            return HttpResponse("评论内容不能为空111")
        user = MyUser.objects.filter(id=request.user.id).first()
        comment2 = Comment.objects.create(
            content=content,
            article_id=aid,
            author_id=request.user.id,
            create_time=timezone.now(),
            user=user,
            parent_comment=comment1
        )
        
                # 触发WebSocket通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'article_{aid}',
            {
                'type': 'new_comment',
                'content': content,
                'user': user.username,
                'comment_id': comment2.id,
                'parent_comment_id': comment_id
            }
        )
        return redirect(reverse('articledetail', kwargs={'id': request.user.id, 'aid': aid}))


# def create_article(request):
#     if request.method == 'POST':
#         form = ArticleForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('article_list')
#     else:
#         form = ArticleForm()
#     return render(request, 'article_create.html', {'form': form})


from django.db.models import Q
def search_view(request,page,id):
    '''
    搜索帖子
    :param request:
    :return:
    '''
    user=MyUser.objects.filter(id=id).first()
    
    keyword=request.POST.get('v')
    if keyword:
        articles = Article.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword) |Q(abstract__icontains=keyword) 
        ).order_by('-create_time')
    else:
        articles=Article.objects.none() # 如果没有关键字，返回空查询集
        
    context = {
    'articles': articles,
    'v': keyword,
    'id':user.id
}
    return render(request,'search.html',context)

@login_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article', id=request.user.id, page=1, typeId=0)
    else:
        form = ArticleForm()
    return render(request, 'article_create.html', {'form': form})


from .utils import view_counter
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def hot_articles(request, id):
    """热门文章排行榜"""
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    
    # 使用缓存，每5分钟更新一次
    cache_key = f'hot_articles_{id}'
    hot_articles_data = cache.get(cache_key)
    
    if not hot_articles_data:
        # 从Redis获取热门文章ID和分数
        top_articles_data = view_counter.get_top_articles(20)
        
        # 修复：解析出文章ID
        article_ids = []
        for item in top_articles_data:
            # 示例：b'article:1:views' -> 提取 "1"
            try:
                # 解码字节串并分割
                parts = item[0].decode().split(':')
                # parts = ["article", "1", "views"]
                article_id = int(parts[1])  # 提取数字部分
                article_ids.append(article_id)
            except (IndexError, ValueError) as e:
                logger.error(f"解析文章ID失败: {item[0]}, 错误: {e}")
                continue
        
        # 批量获取文章对象
        articles = Article.objects.filter(id__in=article_ids)
        article_map = {article.id: article for article in articles}
        
        # 构建带排序分数的文章列表
        hot_articles_data = []
        for article_id, score in top_articles_data:
            if article_id in article_map:
                article = article_map[article_id]
                article.realtime_views = score  # 动态添加阅读量属性
                hot_articles_data.append(article)
        
        # 缓存5分钟
        cache.set(cache_key, hot_articles_data, 300)
    
    return render(request, 'hot_articles.html', {
        'hot_articles': hot_articles_data,
        'id': id
    })