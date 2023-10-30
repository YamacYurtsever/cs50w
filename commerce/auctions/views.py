from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from datetime import datetime
from .models import User, Listing, Watchlisted, Bid, Comment

categories = ["Fashion", "Toys", "Electronics", "Home", "Furniture", "Books", "Art", "Collectibles", "Sports Equipment",
              "Jewelry", "Automotive", "Music Instruments", "Computers", "Mobile Phones", "Video Games", "Appliances",
              "Antiques", "Crafts", "Outdoor", "Pets", "Office Supplies", "Baby & Kids", "Health & Beauty", "Tools & Equipment",
              "Food & Beverage", "Travel", "Tickets", "Services", "Miscellaneous"]


def index(request):
    listings = Listing.objects.filter(closed=False).order_by("-datetime")

    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        # Get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid_price = request.POST["starting-bid"]
        category = request.POST["category"]

        # Check if any of the required fields are empty
        if not title or not description or not starting_bid_price or not category:
            return render(request, "url 'create'", {
                "message": "There is an empty field"
            })

        # Check if the category is one of the possible categories
        if category not in categories:
            return render(request, "url 'create'", {
                "message": "Category doesn't exist"
            })

        # Try to convert the starting bid into an int
        try:
            starting_bid_price = int(starting_bid_price)
        except ValueError:
            return render(request, "url 'create'", {
                "message": "Starting bid in wrong format"
            })

        # Check if starting bid is negative
        if starting_bid_price < 0:
            return render(request, "url 'create'", {
                "message": "Starting bid can not be negative"
            })

        # Create listing object and save it to the database
        newListing = Listing(
            title=title,
            description=description,
            category=category,
            datetime=datetime.now(),
            user=request.user
        )

        # Handle image
        try:
            image = request.FILES["image"]
            if image:
                newListing.image = image
        except:
            pass
        newListing.save()

        # Add new starting bid to the database
        Bid.objects.create(user=request.user,
                           listing=newListing, price=starting_bid_price)

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create.html", {
            "categories": sorted(categories)
        })


def listing(request, id):
    # Get the listing object
    try:
        thisListing = Listing.objects.get(listing_id=id)
    except Listing.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    # Get the comments
    comments = Comment.objects.filter(listing=thisListing)

    # Open the listing page
    if request.user.is_authenticated:
        watchlist = Watchlisted.objects.filter(user=request.user)
        isWatchlisted = any(watchlisted.listing ==
                            thisListing for watchlisted in watchlist)
        return render(request, "auctions/listing.html", {
            "listing": thisListing,
            "comments": comments,
            "isWatchlisted": isWatchlisted
        })
    else:
        return render(request, "auctions/listing.html", {
            "comments": comments,
            "listing": thisListing,
        })


@login_required
def watchlistManager(request):
    watchlist = Watchlisted.objects.filter(user=request.user)

    if request.method == "POST":
        id = request.POST["id"]

        if id:
            try:
                # Check if a listing with that id is found in the database
                thisListing = Listing.objects.get(listing_id=id)

                if Watchlisted.objects.filter(user=request.user, listing=thisListing).exists():
                    # Remove listing from the watchlist
                    Watchlisted.objects.filter(
                        user=request.user, listing=thisListing).delete()

                else:
                    # Add listing to the watchlist
                    Watchlisted.objects.create(
                        user=request.user, listing=thisListing)

            except Listing.DoesNotExist:
                pass

    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


@login_required
def makeBid(request):
    # Get the attributes of bid
    user = request.user
    id = request.POST["id"]
    price = request.POST["price"]

    # Check if any of the post request fields are empty
    if not id or not price:
        return HttpResponseRedirect(reverse("index"))

    # Check if id and price is in the correct format
    try:
        listing = Listing.objects.get(listing_id=id)
        price = int(price)
    except:
        return HttpResponseRedirect(reverse("index"))

    # Check if the price is lower than the price of the highest bid
    if price <= listing.highest_bid.price:
        return HttpResponseRedirect(reverse("index"))

    # Add new bid to the database
    Bid.objects.create(user=request.user,
                       listing=listing, price=price)

    return HttpResponseRedirect(reverse("listing", args=[id]))


@login_required
def closeAuction(request):
    id = request.POST["id"]
    if not id:
        return HttpResponseRedirect(reverse("listing", args=[id]))

    try:
        listing = Listing.objects.get(listing_id=id)
    except:
        return HttpResponseRedirect(reverse("listing", args=[id]))

    listing.closed = True
    listing.save()

    return HttpResponseRedirect(reverse("listing", args=[id]))


@login_required
def comment(request):
    id = request.POST["id"]
    content = request.POST["content"]
    if not id or not content:
        return HttpResponseRedirect(reverse("listing", args=[id]))

    try:
        listing = Listing.objects.get(listing_id=id)
    except:
        return HttpResponseRedirect(reverse("listing", args=[id]))

    Comment.objects.create(user=request.user,
                           listing=listing,
                           content=content)

    return HttpResponseRedirect(reverse("listing", args=[id]))


def openCategories(request, category=None):
    if category:
        if not category in categories:
            return HttpResponseRedirect(reverse("openCategories"))

        listings = Listing.objects.filter(
            category=category).order_by("-datetime")

        return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings
        })
    else:
        return render(request, "auctions/categories.html", {
            "categories": categories
        })
