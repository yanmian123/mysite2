from django.shortcuts import render

# Create your views here.
def link(request,id,page,typeId):
    '''
    查询帖子信息
    '''
    print(id,page,typeId)
    return render(request,'link.html',locals())