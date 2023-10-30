
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    # API Routes
    path("toggle_follow", views.toggle_follow, name="toggle_follow"),
    path("get_username", views.get_username, name="get_username"),
    path("load_all_posts", views.load_all_posts, name="load_all_posts"),
    path("load_profile_posts", views.load_profile_posts, name="load_profile_posts"),
    path("load_following_posts", views.load_following_posts,
         name="load_following_posts"),
    path("update_post", views.update_post, name="update_post"),
    path("toggle_like", views.toggle_like, name="toggle_like"),
    path("check_like", views.check_like, name="check_like")
]
