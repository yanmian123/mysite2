from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from article import consumers
import article.routing  # 导入 article 应用的路由配置
from django.core.asgi import get_asgi_application
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # 原有的 HTTP 处理
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             article.routing.websocket_urlpatterns  # 使用 article 的 WebSocket 路由
#         )
#     ),
# })

websocket_urlpatterns = [
    re_path(r'^ws/article/(?P<article_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
    
]
