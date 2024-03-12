# models.py
from django.contrib.auth.models import AbstractUser
    
class CustomUser(AbstractUser):
    USERNAME_FIELD = 'username'

    def get_username(self):
        return self.username
    
    def __str__(self) -> str:
        return self.username
