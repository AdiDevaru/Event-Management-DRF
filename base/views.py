from django.shortcuts import render, get_object_or_404
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response

from .models import Events
from .serializers import UserProfileSerializer, EventSerializer

from django.contrib.auth import get_user_model
UserProfile = get_user_model()

# USER VIEW SET.
class UserProfileViews(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
#EVENT VIEW SET
class EventViewSet(ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    