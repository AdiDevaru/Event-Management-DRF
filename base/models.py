from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserProfileManager
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

# USER MODEL
class UserProfile(AbstractUser):
    # username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    username = None
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.CharField(max_length=100, default='default_image', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'full_name', 'bio', 'location', 'profile_picture']
    
    objects = UserProfileManager()
    
    def __str__(self):
        return f'ID:{self.id}-{self.full_name}' 
    
# EVENT MODEL
class Events(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
# RSVP Model
class RSVP(models.Model):
    STATUS_CHOICES = [
        ('Going', 'Going'),
        ('Maybe', 'Maybe'),
        ('Not going', 'Not going'),
    ]
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    def __str__(self):
        return f'{self.user} {self.status} for {self.event}'
    
# REVIEW Model
class Review(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(1)])
    comment = models.TextField()
    
    def __str__(self):
        return f'{self.user} rated {self.rating} for {self.event}'
    
    