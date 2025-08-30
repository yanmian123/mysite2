# from django.http.response import HttpResponse, JsonResponse

# def echo(request,*args, **kwargs):
#     """
#     测试函数
#     :param request:
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     data=request.GET
#     ret_value=data.get('name','world')
#     return HttpResponse(ret_value,content_type='text/plain')

# def my_view(request):
#     # 设置会话数据
#     request.session['user_id'] = 123
#     request.session['username'] = 'john'
    
#     # 获取会话数据
#     user_id = request.session.get('user_id')
    
#     # 删除会话数据
#     if 'username' in request.session:
#         del request.session['username']
    
#     return HttpResponse(request.session.get('user_id',"defaultvalue"))
