"""
ASGI config for mysite2 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# your_project/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite2.settings')
# 初始化Django应用
django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from article.routing import websocket_urlpatterns as article_ws_patterns
from concerns.routing import websocket_urlpatterns 


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns+article_ws_patterns)
    ),
})
print(f"[ASGI] Configured WebSocket routes: {websocket_urlpatterns + article_ws_patterns}")

# import os
# from django.core.asgi import get_asgi_application
# from .routing import application  # 导入上一步创建的路由配置

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# # 确保使用新的路由配置
# application = application
