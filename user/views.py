from django.shortcuts import render,redirect
from .models import MyUser
from django.contrib.auth import logout, login as auth_login, authenticate  # Import the logout, login, and authenticate functions
from django.urls import reverse  # Import the reverse function
from django_redis import get_redis_connection  # Import get_redis_connection for Redis operations


# Create your views here.
def tologinpage(request):
    '''
    登录页面
    '''

    return render(request, 'login.html')

def toregisterpage(request):
    '''
    注册页面
    '''
    return render(request, 'register.html')


def register(request):
    """
    用户注册
    :param request:
    :return:
    """
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')
    if MyUser.objects.filter(username=username):
        info = '用户名已存在！'
    elif password2 != password:
        info = '确认密码不正确！'
    else:
        d = {
            'username': username, 'password': password,
            'is_superuser': 0, 'is_staff': 1
        }
        user = MyUser.objects.create_user(**d)
        user.save()
        info = '注册成功，请重新登录！'
        logout(request)
    return render(request, 'register.html', locals())


def login(request):
    """
    用户登录验证
    :param request:
    :return:
    """
    errorInfo = ''
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    
    
    if MyUser.objects.filter(username=username):
        user = authenticate(username=username, password=password)
        if user:
            uuid = request.POST.get('uuid')
            code = request.POST.get('code')
            redis_conn = get_redis_connection('verify_code')
            real_code = redis_conn.get(uuid)
            if not real_code or code != real_code.decode():
            # 验证码错误
                 errorInfo='验证码错误'
            elif user.is_active:
                auth_login(request, user)
                print("登录认证成功，跳转到博客主页")
                kwargs={'id':request.user.id,'page':1,'typeId':0}
                return redirect(reverse('article',kwargs=kwargs))
            else:
                errorInfo = '用户已经被封禁！'

        else:
            errorInfo = '密码错误！'
    elif username:
        errorInfo = '用户名错误！'  


    return render(request, 'login.html', locals())

def about(request,id):
    """
    关于我们
    :param request:
    :return:
    """
    aboutInfo=MyUser.objects.filter(id=id).first()
    print()
    return render(request, 'about.html', locals())