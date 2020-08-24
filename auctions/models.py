from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"
    



#what is better: a bid to have an auction or an aunction to have a bid?
#test1: an auction have a bid

#a bid have a price, owner
class Bid(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

#comment must have an owner, content, auction
class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)

CATEGORIES_CHOICES = (
    ('Tecnology','TECNOLOGY'),
    ('Automotive', 'AUTOMOTIVE'),
    ('Toys','TOYS'),
    ('Fashion','FASHION'),
    ('Books','BOOKS'),
    ('Pet Shop','PET SHOP'),
    ('Watches','WATCHES'),
    ('Antique','ANTIQUE'),
    ('Music Instruments','MUSIC INTRUMENTS'),
)

#an auction have a title, small information, imageurl, category, list of bids, owner, comments, boolean to check if is active
class AuctionListing(models.Model):
    title = models.CharField(max_length=30)
    info = models.CharField(max_length=100)
    imgUrl = models.CharField(max_length=300)
    category = models.CharField(max_length=17, choices=CATEGORIES_CHOICES )
    #the index of an array, maybe

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    bids = models.ManyToManyField(Bid, blank=True, related_name="bids")    
    comments = models.ManyToManyField(Comment, blank=True, related_name="comments")

    isActive = models.BooleanField()

    isWatchOfThoseUsers = models.ManyToManyField(User, blank=True, related_name="usersWatch")
    

