from django.urls import re_path

from apps.games.consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'^game-(?P<room>\d+)/$', GameConsumer.as_asgi()),
]

