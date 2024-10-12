from django.contrib import admin
from .models import UserProfile, Events, RSVP

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Events)
admin.site.register(RSVP)