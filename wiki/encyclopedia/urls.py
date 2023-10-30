from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search_results", views.search_results, name="search_results"),
    path("add", views.add, name="add"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("random", views.random_entry, name="random"),
    path("<str:title>", views.entry, name="entry")
]
