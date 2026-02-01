from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username