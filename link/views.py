from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.
@login_required(login_url='tologinpage') 

def link(request,id,page,typeId):
    '''
    查询帖子信息
    '''
    if request.user.id != id:
        return redirect(reverse('tologinpage'))
    print(id,page,typeId)
    return render(request,'link.html',locals())