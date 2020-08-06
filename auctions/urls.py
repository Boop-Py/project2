from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("closedlistings", views.closed_listings, name="closed_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addlisting", views.add_listing, name="add_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.category, name="categories"),
    path("comment/<str:title>", views.comment, name ="comment"),
    path("category/<str:category>", views.sort_by_category, name="sort_by_category"),
    path("<str:title>", views.auction_details, name="auction_details"),
    path("watchlistadd/<str:title>", views.add, name="add"),
    path("watchlistremove/<str:title>", views.remove, name="remove"),
    path("bidding/<str:title>", views.bidding, name="bidding"),
    path("closed/<str:title>", views.closed, name="closed"),
    path("todolist", views.todolist, name="todolist")
]
