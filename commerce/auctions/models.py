from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    category = models.CharField(max_length=20)
    image = models.ImageField(upload_to="auctions/",
                              default="auctions/default_image.png")
    datetime = models.DateTimeField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    highest_bid = models.ForeignKey(
        'Bid', null=True, blank=True, on_delete=models.SET_NULL, related_name="highest_bid")
    bid_count = models.IntegerField(null=True)
    closed = models.BooleanField(default=False)

    def refresh(self):
        self.highest_bid = Bid.objects.filter(
            listing=self).order_by('-price').first()
        self.bid_count = Bid.objects.filter(listing=self).count() - 1
        self.save()


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.IntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.listing.refresh()


class Watchlisted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
