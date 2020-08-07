from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import operator

from .models import User, Listing, Comment, Bid
from .forms import Comment_Form, Bid_Form



def index(request):
    return render(request, "auctions/index.html", 
                   {"listing": Listing.objects.filter(status="ACTIVE").order_by("-listing_date")})

def closed_listings(request):
    return render(request, "auctions/closedlistings.html",
                    {"listing": Listing.objects.filter(status="CLOSED").order_by("listing_date")})

def auction_details(request, title):
    # retrieve details from db using title
    listing = Listing.objects.filter(title=title).first()
    # check if closed 
    if listing.status is "CLOSED":
        return HttpResponseRedirect ("auctions/closed_listings")
    # retrieve bids in order of date    
    bids = Bid.objects.filter(list=listing).order_by("-bid_date")
    bids_list = []
    # get name of current user
    current_user = request.user
    #list of all bids
    for b in bids:
        bid = b.bid
        bids_list.append(bid)
    if bids_list != []:
        # make max number the current price
        current_price = max(bids_list)
    else:
        # set current price to the start price if no bids
        current_price = listing.start_bid
    if current_user == listing.owner:
        messages.add_message(request, messages.SUCCESS, "If you close your listing, it will be sold to the highest bidder")
        return render(request, "auctions/listownerspage.html",
                      {"l": listing, 
                       "form": Comment_Form,
                       "comments": Comment.objects.filter(list=listing), 
                       "bids": bids,
                       "bid_form": Bid_Form, 
                       "current_price": current_price
                       })                  
    return render(request, "auctions/auction_details.html",
                      {"l": listing, 
                       "form": Comment_Form,
                       "comments": Comment.objects.filter(list=listing), 
                       "bids": bids,
                       "bid_form": Bid_Form, 
                       "current_price": current_price
                       })                      
     
@login_required(login_url="auction/login")     
def add_listing(request):
    current_user = request.user
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        start_bid = request.POST["start_bid"]
        img = request.POST["img"]      
        # save without img if none provided
        if img is None:
            Listing.objects.create(
            title = title, 
            description = description, 
            start_bid = start_bid,
            current_price = start_bid,
            category = category, 
            owner = current_user)
        else: 
            Listing.objects.create(
            title = title, 
            description = description, 
            start_bid = start_bid, 
            current_price = start_bid,
            category = category, 
            owner = current_user,
            img = img)
        messages.add_message(request,messages.SUCCESS, "Your listing is created succesfully")
        return HttpResponseRedirect("/auctions/")
    else:
        return render(request,"auctions/addlisting.html")
 
@login_required(login_url="auctions/login") 
def watchlist(request):
   if "watch" not in request.session:
       request.session["watch"] = []
       return render(request, "auctions/watchlist.html", 
                        {"watchlists": request.session["watch"]})
   else:
       watchlist = request.session["watch"]
       return render(request, "auctions/watchlist.html", 
                        {"watchlists": watchlist})                       
 
@login_required(login_url="auctions/login")  
def add(request, title):
    watchlists = Listing.objects.filter(title=title).first()
    if "watch" not in request.session:
        request.session["watch"] = []
    if watchlists.title in request.session["watch"]:
        messages.add_message(request, messages.SUCCESS, "This item is in already in your watchlist")
        return HttpResponseRedirect("auctions/watchlist")
    request.session["watch"] += [watchlists.title]
    request.session.modified = True
    messages.add_message(request, messages.SUCCESS,"Successfully added to your watchlist!")
    return render(request, "auctions/watchlist.html", 
                    {"watchlists": request.session["watch"]})                   

@login_required(login_url="auctions/login")     
def remove(request, title):
    watchlists = Listing.objects.filter(title=title).first()
    try:
        request.session["watch"].remove(watchlists.title)
    except:
        messages.add_message(request, messages.WARNING, "This item is not in your watchlist")
        return HttpResponseRedirect("auctions:watchlist")
    messages.add_message(request,messages.SUCCESS, "Successfully removed from your watchlist!")
    request.session.modified = True

    return render(request, "auctions/watchlist.html", 
                    {"watchlists": request.session["watch"]})

def category(request):
    all_items = Listing.objects.all()
    categories = []
    for item in all_items:
        category = item.category
        if category not in categories:
            categories.append(category)
    return render(request,"auctions/category.html", 
                    {"categories": categories})

def sort_by_category(request, category):
    items_in_category = Listing.objects.filter(category=category, status="ACTIVE")
    return render(request, "auctions/index.html", 
                    {"listing": items_in_category})
                                     
@login_required(login_url="auctions/login") 
def comment(request, title):
    if request.method == "POST":
       form = Comment_Form(request.POST)
       user = request.user
       listing = Listing.objects.filter(title=title).first()
       if form.is_valid():
           comment = form.cleaned_data["comment"]
           Comment.objects.create(
           user = user, 
           list = listing, 
           comment = comment)
           return HttpResponseRedirect("/auctions/"+ title)
    else:
        return HttpResponseRedirect("/auctions/")

@login_required(login_url="auctions/login") 
def bidding(request, title):
    if request.method == "POST":
        listing = Listing.objects.filter(title=title).first()
        bids = Bid.objects.filter(list=listing)
        bids_list = []
        user_list = []
        for b in bids:
            bid = b.bid
            bids_list.append(bid)
            u = b.user
            user_list.append(u)
        if bids_list != []:
            current_price = max(bids_list)
        else:
            current_price = listing.start_bid
        form = Bid_Form(request.POST)
        user = request.user
        if form.is_valid():
           last_bid = form.cleaned_data["bid"]
           if current_price >= last_bid:
               messages.add_message(request, messages.WARNING, "Please bid higher")
               return HttpResponseRedirect("/auctions/" + title)
           else:
               Bid.objects.create(
               user = user, 
               list = listing, 
               bid = last_bid)
               messages.add_message(request, messages.WARNING, "Succesfully bid on item")
               return HttpResponseRedirect("/auctions/" + title)
        else:
           messages.add_message(request, messages.WARNING, "Invalid form")
           return render(request, "auctions/pagedetails.html",
                            {"l": listing, 
                            "form": Comment_Form,
                            "comments": Comment.objects.filter(list=listing), 
                            "bids": bids,
                            "bid_form": Bid_Form, 
                            "current_price": current_price
                            })
    else:
        return HttpResponseRedirect("auctions/")
    
def closed(request, title):
    listing = Listing.objects.filter(title=title).first()
    bids = Bid.objects.filter(list=listing).order_by("-bid_date")
    bids_list = {}
    current_user = request.user
    for p in bids:
        bid = p.bid
        bid_owner = p.user
        bids_list.update({bid_owner: bid})
    if bids_list != {}:
        current_price = max(bids_list.values())
        winner = max(bids_list.items(), key=operator.itemgetter(1))[0]
    else:
        current_price = listing.start_bid
        winner = "No Winner"      
    listing.status = "CLOSED"
    listing.save()
    if current_user == winner:
        messages.add_message(request, messages.SUCCESS,
                             "You won this auction!")
    if not messages:
        messages.add_message(request, messages.SUCCESS,
                         "Succesfully closed listing")
    return render(request, "auctions/closed.html",
                    {"l": listing, 
                    "form": Comment_Form,
                    "comments": Comment.objects.filter(list=listing), 
                    "bids": bids,
                    "current_price": current_price,
                    "winner": winner
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))

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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")    
        
def todolist(request):
    return render(request, "auctions/todolist.html")