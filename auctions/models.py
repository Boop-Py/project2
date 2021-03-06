from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    CATEGORIES = (
        ("Home, Garden + Accessories", "Home, Garden + Accessories"),
        ("Sport, Leisure + Outdoor", "Sport, Leisure + Outdoor"),
        ("Fashion + Accessories", "Fashion + Accessories"),
        ("Health + Beauty", "Health + Beauty"),
        ("Baby, Children + Toys", "Baby, Children + Toys"),
        ("Vehicles, Parts + Accessories", "Vehicles, Parts + Accessories"),
        ("Electronics + Accessories", "Electronics + Accessories")
    )
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("CLOSED", "Closed")
    )
    title = models.CharField(max_length=64, default=None)
    description = models.CharField(max_length=500, default=None)
    start_bid = models.IntegerField()
    img = models.ImageField(null=True, blank=True)
    category = models.CharField(blank=True, choices=CATEGORIES, max_length=32)
    listing_date = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listowner", default=None, blank=True, null=True)
    status = models.CharField(blank=True, choices=STATUS_CHOICES, max_length=32, default="ACTIVE")
    current_price = models.IntegerField(default=0)

    def __str__(self):
        return f"Title : {self.title} " \
               f"Description : {self.description} " \
               f"Category : {self.category} "\
               f"Start bid : {self.start_bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member", default=None)
    list = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing", null=True)
    comment = models.CharField(max_length=250, null=True)
    comment_date = models.DateTimeField(auto_now=True)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner", default=None)
    list = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="list", null=True)
    bid = models.IntegerField(default=0)
    bid_date = models.DateTimeField(auto_now=True)
    