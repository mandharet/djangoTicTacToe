from django.urls import include, re_path
from . import views

urlpatterns = [
    re_path(r'^game-(?P<pk>\d+)/$', views.GameView.as_view(), name='game'),
    re_path(r'^$', views.NewGameView.as_view(), name='new-game'),
]
