from django.contrib import admin
from .models import UserProfile, Events, RSVP, Review, Invitations

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Events)
admin.site.register(RSVP)
admin.site.register(Review)
admin.site.register(Invitations)