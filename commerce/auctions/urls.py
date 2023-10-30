from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlistManager, name="watchlist"),
    path("bid", views.makeBid, name="bid"),
    path("close", views.closeAuction, name="close"),
    path("comment", views.comment, name="comment"),
    path("categories", views.openCategories, name="categories"),
    path("categories/<str:category>", views.openCategories, name="category"),
    path("<int:id>", views.listing, name="listing")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
