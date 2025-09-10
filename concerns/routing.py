# routing.py
from django.urls import re_path

from .consumer import ConcernConsumer

websocket_urlpatterns = [
    re_path(r"ws/user_(?P<user_id>\d+)/$", ConcernConsumer.as_asgi()),
]