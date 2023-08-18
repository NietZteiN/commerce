from re import A
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import User, Listing, Comment, Bid


def index(request):
    return render(request, "auctions/index.html", {
              "listings": Listing.objects.all()
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



def create(request): 
    if request.method == "POST": 
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["url"]
        category = request.POST["category"]
        owner = request.user

        f = Listing(title=title, description=description, minimumbid=starting_bid, 
                    image=image, category=category, owner=owner, closed=False)
        f.save()
        return HttpResponseRedirect(reverse("index"))

           
    return render(request, "auctions/create.html")


def listing(request, listing_id): 

    user = request.user 

    try: 
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist: 
        raise Http404("Listing not found.")

    comments = listing.comments.all() 
    owner = listing.owner
    if user.username == owner.username: 
        owner_signed_in = True
    else: 
        owner_signed_in = False 

    if listing.closed == True: 
        winner = listing.winner 
        return render(request, "auctions/listing.html", {
                "listing": listing, 
                "comments": comments,
                "owner_signed_in": owner_signed_in, 
                "message": True, 
                "winner": winner, 
            })

    return render(request, "auctions/listing.html", {
            "listing": listing, 
            "comments": comments,
            "owner_signed_in": owner_signed_in, 
        })

def categories(request): 
    categories = ["FA", "TO" ,"EL", "HO", "GA", "MI"]
    category = request.POST.get("cat")

    if category is not None and category in categories:
        return render(request, "auctions/categories.html", {
            "listings": Listing.objects.filter(category=category), 
            "categories": categories
        })

    return render(request, "auctions/categories.html", {
            "categories": categories, 
        })

def wishlist(request): 

    user = request.user

    return render (request, "auctions/wishlist.html", {
            "listings": user.listings.all(), 
        })

def wish(request, listing_id): 
    
    if request.method == "POST": 
        user = request.user
        listing = Listing.objects.get(pk=listing_id)
        if listing in user.listings.all(): 
            user.listings.remove(listing)
        else: 
            user.listings.add(listing)
        return HttpResponseRedirect(reverse("wishlist"))

def comment(request, listing_id): 
    if request.method == "POST": 
        user = request.user
        listing = Listing.objects.get(pk=listing_id)
        content = request.POST["content"]
        c = Comment(user=user, listing=listing, content=content)
        c.save()

        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def bid(request, listing_id): 
    if request.method == "POST": 
        user = request.user
        listing = Listing.objects.get(pk=listing_id)
        value = int(request.POST.get("value"))
        minval = listing.minimumbid
        if value > minval: 
            b = Bid(user=user, listing=listing, value=value)
            b.save()
            listing.minimumbid = value 
            listing.save()
        else: 
            raise Http404("Bid not high enough.")

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def close(request, listing_id): 
    if request.method == "POST": 
        listing = Listing.objects.get(pk=listing_id)

        try: 
            highest_bid = listing.bids.aggregate(Max('value'))
            highest_bid_value = highest_bid['value__max']
            winner_bid = listing.bids.get(value=highest_bid_value)
            winner = winner_bid.user
            
            listing.closed = True
            listing.winner = winner
            listing.save() 
        except Bid.DoesNotExist: 
            listing.closed = True
            listing.winner = request.user
            listing.save()

        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))