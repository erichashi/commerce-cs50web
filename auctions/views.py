from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.db.models import Max

#super user: eric, pass: eric123

from .models import User, AuctionListing, Bid, Comment
from .forms import placeBid, placeComment

#Helpers
def getHiguestBid(bids):
    higuestBid = Bid(0, None)
    highvalue= 0
    for bid in bids:
        if bid.price > highvalue:
            highvalue = bid.price
            higuestBid = bid
    return higuestBid

def valueIsGreaterThanOtherBids(value, listing_id):
    single = AuctionListing.objects.get(id=listing_id)
    bids = single.bids.all()
    for bid in bids:
        if bid.price >= value:
            return False
    return True

def getLenBids(bids):
    return len(bids)

def isInWatch(listing_id, user):
    # try:
    userList = AuctionListing.objects.get(id=listing_id).isWatchOfThoseUsers.all()

    if str(user) in str(userList):
        return True
        
    return False

def addOrRemove(single_id, user):
    try:
        if isInWatch(single_id, user):
            return "Remove"
        else:
            return "Add"
    except User.DoesNotExist:
        return ""

def initializeMaxBid(objects):
    listings = []
    for l in objects:
        bid = getHiguestBid(l.bids.all())
        l.higuestbid = bid.price
        listings.append(l)
    return listings

def initializeListingInfo(single, listing_id, user):
    c = {
        "listing": single,
        "comments": single.comments.all(),
        "bids": single.bids.all(),
        "higuestBid": getHiguestBid(single.bids.all()),
        "lenBids": getLenBids(single.bids.all()),
        "addOrRemove": addOrRemove(listing_id, user), 
        "placeComment": placeComment(prefix='comment'),
        "placeBid": placeBid(prefix='bid'),
    }
    return c

#index
def index(request):
    return render(request, "auctions/index.html", {
        "auctions": initializeMaxBid(AuctionListing.objects.filter(isActive= True)),
        "title": "Auction Listing"
    })

#Given functions: 
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


#Functions

def listing(request, listing_id):
    #submit comment or bid

    try:
        single = AuctionListing.objects.get(id=listing_id)
        c = initializeListingInfo(single, listing_id, request.user)
        t = 'auctions/singlelisting.html'

    except AuctionListing.DoesNotExist:
        raise Http404("Listing not found")

    if request.method == 'POST':
    
        #submit bid
        if "submitBid" in request.POST:        
            placeBidForm = placeBid(request.POST, prefix='bid')
            if placeBidForm.is_valid():
                value = placeBidForm.cleaned_data["bid"]
                if valueIsGreaterThanOtherBids(value, listing_id):
                    user = request.user
                    bid = Bid(price=value, owner=user)
                    bid.save()                

                    listing = AuctionListing.objects.get(id=listing_id)
                    listing.bids.add(bid)
                    #when adding bid, page do not reload
                    cb = initializeListingInfo(listing, listing_id
                    , request.user)

                    return render(request, t, cb)
                else:
                    c["message"] = 'Bid must be greater than other bids'
                    return render(request, t, c)

            else:
                c['placeBid'] = placeBidForm
                return render(request, t, c)
                
            

        #submit comment
        elif 'submitComment' in request.POST:
            placeCommentForm = placeComment(request.POST, prefix='comment')

            if placeCommentForm.is_valid():
                content = placeCommentForm.cleaned_data["content"] 

                user = request.user
                comment = Comment(content=content, owner=user)
                comment.save()

                listing = AuctionListing.objects.get(id=listing_id)
                listing.comments.add(comment)

                return render(request, t, c)
            else:
                c['placeComment'] = placeCommentForm
                return render(request, t, c)

    else:
        return render(request, t, c)


categories = [
    'Technology', 'Automotive', 'Toys', 'Sports', 'Fashion', 'Music Instruments', 'Books', 'Pet Shop', 'Watches', 'Antique'
]

@login_required
def create(request):
    if request.method == 'POST':
        title = request.POST["title"]
        info = request.POST["info"]
        imgUrl = request.POST["img"]
        startingBid = request.POST["sbid"]
        category = request.POST["select"]

        owner = request.user
        print('the username is: '+owner.username)
        
        bid = Bid(price=startingBid, owner=owner)
        bid.save()

        listing = AuctionListing(title=title, info=info, imgUrl=imgUrl, category=category, owner=owner, isActive=True)

        listing.save()
        listing.bids.add(bid)


        return HttpResponseRedirect(reverse("index"))


    else:
        return render(request, "auctions/create.html", {
            "categories": categories
        })


@login_required
def dealwatch(request, listing_id):

    listing = AuctionListing.objects.get(id=listing_id)
    
    if not isInWatch(listing_id, request.user):
        #add to wacth

        listing.isWatchOfThoseUsers.add(request.user)
    else:
        #remove from watch

        listing.isWatchOfThoseUsers.remove(request.user)
        listing.save()
    
    return HttpResponseRedirect(reverse("watchlist"))


def watchlist(request):
    return render(request, "auctions/index.html", {
        "auctions": initializeMaxBid(AuctionListing.objects.filter(isWatchOfThoseUsers__in =[request.user], isActive=True)),
        "title": "Watchlist"
    })





def category(request):
    return render(request, "auctions/category.html", {
        "categories": categories,
    })

def filter(request, category):
    return render(request, "auctions/index.html", {
        "auctions": initializeMaxBid(AuctionListing.objects.filter(category__exact=category)),    
        "title": "Auction Listing: "+category 
    })

@login_required
def close(request, listing_id):
    single = AuctionListing.objects.get(id=listing_id)

    single.isActive = False
    single.save()

    c = {
        "listing": single,
        "comments": single.comments.all(),
        "bids": single.bids.all(),
        "higuestBid": getHiguestBid(single.bids.all()),
        "lenBids": getLenBids(single.bids.all()),
        "AddOrRemove": "Add or Remove", #check_watchlist(listing_id),
        "placeComment": placeComment(prefix='comment'),
        "placeBid": placeBid(prefix='bid'),
    }
    t = 'auctions/singlelisting.html'
    return render(request, t, c)
