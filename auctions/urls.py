from django.urls import path

from . import views

urlpatterns = [
    #given
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    #create listing
    path("create", views.create, name="create"),

    #listing page
    path("listing/<int:listing_id>", views.listing, name="listing"),

    path("close/<int:listing_id>", views.close, name="close"),
    

    #watchlist
    path("watchlist", views.watchlist, name="watchlist"),
    path("addwatchlist/<int:listing_id>", views.dealwatch, name="dealwatch"),

    #categories
    path("category", views.category, name="category"),
    path("listing/<str:category>", views.filter, name="filter"),

]
