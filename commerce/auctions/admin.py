from django.contrib import admin

from .models import Listing, Watchlisted, Bid, Comment

# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Watchlisted)
admin.site.register(Comment)
