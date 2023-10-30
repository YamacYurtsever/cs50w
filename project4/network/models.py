from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    followers = models.ManyToManyField(
        "self", related_name="following", symmetrical=False)


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=300)
    datetime = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    liked_users = models.ManyToManyField(
        "User", related_name="liked_posts")
