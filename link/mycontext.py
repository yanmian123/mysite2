from .models import LinkInfo

def getAllLink(request):
    '''
    获取友情链接
    '''
    
    return {"linklist":LinkInfo.objects.all()}