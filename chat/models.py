from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager

# Create your models here.


class User(AbstractUser):
    username = None
    
    email = models.EmailField('email address', unique=True)
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='members')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def likes(self):
        return self.likemessage_set.count()
    
    @property
    def liked_by_user(self):
        return self.likemessage_set
    
    @property
    def message_by(self):
        return self.created_by


class LikeMessage(models.Model):
    id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def liked_by(self):
        return self.created_by


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    user = models.ForeignKey(User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")
