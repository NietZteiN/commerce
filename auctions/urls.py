from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"), 
    path("create", views.create, name="create"),
    path("<int:listing_id>", views.listing, name="listing"), 
    path("<int:listing_id>/bid", views.bid, name="bid"), 
    path("<int:listing_id>/wish", views.wish, name="wish"), 
    path("<int:listing_id>/comment", views.comment, name="comment"), 
    path("<int:listing_id>/close", views.close, name="close"), 
    path("categories", views.categories, name="categories"), 
    path("wishlist", views.wishlist, name="wishlist"), 
]
