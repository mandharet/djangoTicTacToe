from django.contrib import admin

from . import models


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    list_display = 'id', 'finished', 'created', 'size', 'min_length', 'allow_horizontal', \
                   'allow_vertical', 'allow_diagonal',
