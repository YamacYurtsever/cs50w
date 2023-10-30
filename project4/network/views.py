import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import datetime

from .models import User, Post


def index(request):
    if request.method == "POST":
        content = request.POST["content"]
        if content:
            Post.objects.create(user=request.user, content=content)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "network/index.html")


def load_all_posts(request):
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))

    posts = list(Post.objects.all().order_by("-datetime")[start:end].values())

    return JsonResponse({"posts": posts})


def profile(request, username):
    user = User.objects.get(username=username)
    followers = user.followers.all()
    following = user.following.all()
    return render(request, "network/profile.html", {
        "username": username,
        "followers": followers,
        "following": following
    })


def load_profile_posts(request):
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))

    username = request.GET.get("username")
    user = User.objects.get(username=username)

    posts = list(Post.objects.filter(user=user).order_by(
        "-datetime")[start:end].values())

    return JsonResponse({"posts": posts})


@login_required
def following(request):
    return render(request, "network/following.html")


def load_following_posts(request):
    start = int(request.GET.get("start"))
    end = int(request.GET.get("end"))

    following_users = request.user.following.all()
    posts = list(Post.objects.filter(user__in=following_users).order_by(
        "-datetime")[start:end].values())

    return JsonResponse({"posts": posts})


@csrf_exempt
@login_required
def toggle_follow(request):
    # Check if the request is post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the data
    data = json.loads(request.body)
    user_followed_username = data.get("userFollowed")
    user_following_username = data.get("userFollowing")

    try:
        user_followed = User.objects.get(username=user_followed_username)
        user_following = User.objects.get(username=user_following_username)

        # Check if the users exist
        if not user_followed or not user_following:
            return JsonResponse({"error": "There are empty fields."}, status=400)

        if user_followed.followers.filter(username=user_following_username):
            # User is followed, unfollow
            user_followed.followers.remove(user_following)
            return JsonResponse({"message": "User unfollowed successfully."}, status=200)

        else:
            # User is not followed, follow
            user_followed.followers.add(user_following)
            return JsonResponse({"message": "User followed successfully."}, status=200)
    except:
        return JsonResponse({"error": "User does not exist."}, status=400)


def get_username(request):
    user_id = int(request.GET.get("user_id"))
    try:
        username = User.objects.get(id=user_id).username
        return JsonResponse({"username": username})
    except:
        return JsonResponse({"error": "User not found"})


@csrf_exempt
@login_required
def update_post(request):
    # Check if the request is post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the data
    data = json.loads(request.body)
    post_id = data.get("post_id")
    content = data.get("content")

    # Update post
    try:
        post = Post.objects.get(id=post_id)
        if post.user != request.user:
            return JsonResponse({"error": "You are not the creator of the post."}, status=400)
        post.content = content
        post.datetime = datetime.datetime.now()
        post.edited = True
        # Alter the like things as well when they work
        post.save()
        return JsonResponse({"message": "Post updated successfully."}, status=200)
    except:
        return JsonResponse({"error": "No post with that id."}, status=400)


@csrf_exempt
@login_required
def toggle_like(request):
    # Check if the request is post
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get the data
    data = json.loads(request.body)
    post_id = data.get("post_id")

    # Like or unlike post
    try:
        post = Post.objects.get(id=post_id)
        if request.user not in post.liked_users.all():
            post.liked_users.add(request.user)
            post.likes += 1
            post.save()
            return JsonResponse({"message": "Post liked successfully."}, status=200)
        else:
            post.liked_users.remove(request.user)
            post.likes -= 1
            post.save()
            return JsonResponse({"message": "Post unliked successfully."}, status=200)
    except:
        return JsonResponse({"error": "No post with the id " + post_id}, status=400)


def check_like(request):  # ISSUE HERE
    post_id = int(request.GET.get("post_id"))
    post = Post.objects.get(id=post_id)

    isLiked = request.user in post.liked_users.all()

    return JsonResponse({"isLiked": isLiked})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
