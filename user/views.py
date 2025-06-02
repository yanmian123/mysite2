from django.shortcuts import render,redirect
from .models import MyUser
from django.contrib.auth import logout, login as auth_login, authenticate  # Import the logout, login, and authenticate functions
from django.urls import reverse  # Import the reverse function
from django_redis import get_redis_connection  # Import get_redis_connection for Redis operations
from django.contrib.auth.decorators import login_required

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
    
    remember_me=request.session.get('remember_me',False)
    username = request.session.get('username', '')
    password = request.session.get('password', '')
    if remember_me:
        kwargs={'id':request.user.id,'page':1,'typeId':0}
        request.session.set_expiry(0)
        request.session['remember_me'] = remember_me == 'off'#只保持一次登录
        logout(request)
        return redirect(reverse('article',kwargs=kwargs))
    errorInfo = ''
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    remember_me=request.POST.get('remember_me','')

    
    
    if MyUser.objects.filter(username=username) or MyUser.objects.filter(phone=username):
        user = authenticate(username=username, password=password)
        if user:
            uuid = request.POST.get('uuid')
            code = request.POST.get('code')
            redis_conn = get_redis_connection('verify_code')#连接到名为verify_code的redistribution数据库，settings.py中可以配置
            real_code = redis_conn.get(uuid)
            if not real_code or code != real_code.decode():
            # 验证码错误
                 errorInfo='验证码错误'
            elif user.is_active:
                auth_login(request, user)
                if request.POST.get('remember_me') == 'on':
                    request.session.set_expiry(60 * 60 * 24)  # 1天

                print("登录认证成功，跳转到博客主页")
                kwargs={'id':request.user.id,'page':1,'typeId':0}
                request.session['remember_me'] = remember_me == 'on'
                return redirect(reverse('article',kwargs=kwargs))
            else:
                errorInfo = '用户已经被封禁！'

        else:
            errorInfo = '密码错误！'
    elif username:
        errorInfo = '用户名错误！'  
    


    return render(request, 'login.html', locals())

@login_required(login_url='tologinpage') 
def about(request,id):
    """
    关于我们
    :param request:
    :return:
    """
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    aboutInfo=MyUser.objects.filter(id=id).first()

    editing=request.GET.get('edit')=='true'

    if request.method=='POST' and editing:
        aboutInfo.name = request.POST.get('name', aboutInfo.name)
        aboutInfo.company = request.POST.get('company', aboutInfo.company)
        aboutInfo.birthday = request.POST.get('birthday', aboutInfo.birthday)
        aboutInfo.wx = request.POST.get('wx', aboutInfo.wx)
        aboutInfo.phone = request.POST.get('phone', aboutInfo.phone)
        aboutInfo.address = request.POST.get('address', aboutInfo.address)
        avatar = request.FILES.get('avatar')


        if avatar:
            aboutInfo.avatar = avatar
        aboutInfo.save()
        return redirect(reverse('about', kwargs={'id': id}))
    return render(request, 'about.html', locals())


