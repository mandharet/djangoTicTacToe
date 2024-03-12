from django.db import models
import uuid

# Create your models here.
class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    vacant = models.BooleanField(default=True)
                                       
                                       
class Player(models.Model):
    name= models.CharField(max_length=10, null=False)
    shared_room = models.ForeignKey(Room, on_delete=models.CASCADE)