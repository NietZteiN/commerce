from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    # Because it inherits from AbstractUser, it will already have fields for a username, email, password, etc
    pass

class Listing(models.Model): 

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=5000)
    minimumbid = models.IntegerField(validators=[MinValueValidator(1)])
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    users = models.ManyToManyField(User, blank=True, related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_listings", default=1, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_won", default=1, null=True)
    closed = models.BooleanField(default=False)

    CATEGORIES = [
        ("FA", "Fashion"), 
        ("TO", "Toys"), 
        ("EL", "Electronics"),
        ("HO", "Home"), 
        ("GA", "Games"), 
        ("MI", "Miscellaneous")
    ]
    category = models.CharField(
        max_length = 2, 
        choices=CATEGORIES, 
        default="MI",
    )

    def __str__(self): 
        return f"{self.title}: minimum is {self.minimumbid} [Description: {self.description}]"

class Bid(models.Model): 
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", default=1, null=True)
   listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", default=1, null=True)
   value = models.IntegerField(validators=[MinValueValidator(1)])


class Comment(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", default=1, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", default=1, null=True)
    content = models.CharField(max_length=5000, default="", null=True)

