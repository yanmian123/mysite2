from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.views import View
from django.utils import timezone
from article.models import ArticleType
from .models import Article, MyUser,comment
from .form import ArticleForm
from django.contrib.auth.decorators import login_required
from django_redis import get_redis_connection 

# Create your views here.

@login_required(login_url='tologinpage')
def article(request,id,page,typeId):
    '''
    查询帖子信息
    '''
    # redis_conn = get_redis_connection('c_session')
    # id2=request.user.id
    # print(id2)
    # if id2 != id:
    #     return redirect(reverse('toregisterpage'))
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
@login_required(login_url='tologinpage')                                                 
def articledetail(request,id,aid):
    '''
    查询帖子详情
    :param request:
    :param id: 用户id       
    :param aid: 某个帖子的id
    '''    
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    if request.method=='GET':
        user=MyUser.objects.filter(id=id).first()
        article=Article.objects.filter(id=aid).first() # 查询帖子
        Article.objects.filter(id=aid).update(reads=article.reads+1) # 更新阅读量
        if article==None:   
            return HttpResponse("没有该帖子")
        articlecomment = comment.objects.filter(article_id=aid, parent_comment__isnull=True).order_by('-create_time')
        return render(request,'articledetail.html',locals()) # locals() 函数会返回当前作用域里的所有局部变量，作用是把这些变量传递给 render 函数。
    else:
        # user=request.POST.get('user')
        user=MyUser.objects.filter(id=id).first()
        content=request.POST.get('content')
    # 检查 content 是否为空
        if not content:
            return HttpResponse("评论内容不能为空")
        article = Article.objects.get(id=aid)
        parent_comment_id = request.POST.get('parent_comment_id')
        if parent_comment_id:
            parent_comment = comment.objects.get(id=parent_comment_id)
            value = {
                'user': user,
                'content': content,
                'author_id': id,
                'article_id': aid,
                'create_time': timezone.now(),
                'parent_comment': parent_comment
            }
        else:
            value = {
                'user': user,
                'content': content,
                'author_id': id,
                'article_id': aid,
                'create_time': timezone.now()
            }
        comment.objects.create(**value)
        kwargs = {'id': id, 'aid': aid}
        return redirect(reverse('articledetail', kwargs=kwargs))
    
    

def commentdelete(request, comment_id):
    if request.method == 'POST':
        try:
            comment1 = comment.objects.get(id=comment_id)
            comment1.delete()
        except comment.DoesNotExist:
            pass
        kwargs={'id':comment1.author_id,'aid':comment1.article_id}
    return redirect(reverse('articledetail',kwargs=kwargs)) # 重定向到帖子详情页


def commentreply(request, comment_id, aid):
    if request.method == 'POST':
        try:
            comment1 = comment.objects.get(id=comment_id)
            commentauthor = comment1.author_id
        except comment.DoesNotExist:
            return HttpResponse("评论不存在")
        content = request.POST.get('content')
        if not content:
            return HttpResponse("评论内容不能为空")
        user = MyUser.objects.filter(id=request.user.id).first()
        comment2 = comment.objects.create(
            content=content,
            article_id=aid,
            author_id=commentauthor,
            create_time=timezone.now(),
            user=user,
            parent_comment=comment1
        )
        kwargs = {'id': request.user.id, 'aid': aid}
        return redirect(reverse('articledetail', kwargs=kwargs))


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'article_create.html', {'form': form})


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


