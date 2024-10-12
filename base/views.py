from django.shortcuts import redirect, get_object_or_404
SECRET_KEY = 'adidevaru$@9182'

from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import permissions
from rest_framework.decorators import action

from .models import Events, RSVP
from .serializers import UserProfileSerializer, EventSerializer, RSVPSerializer
from .permissions import IsOwnerOrReadOnly, IsOrganizerOrReadOnly, IsRSVPUserOrReadOnly

from django.contrib.auth import get_user_model
UserProfile = get_user_model()
import jwt
# from pprint import pprint

# USER VIEW SET
class UserProfileViews(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    # Allow non-authenticated users to create a new UserProfile 
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]  
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # Logged in users cannot create a new UserProfile
        if request.user.is_authenticated:
            return Response({'error': 'LOGOUT to register new user'}, status=403)
        
        # Automatically LOGIN new user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        payload = {'id': user.id}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'mssg': 'Successfully logged in'} 
        
        return response
    
    # Delete LOGIN token when user is deleted     
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance == request.user:
            self.perform_destroy(instance)
            response = Response({'detail': 'User deleted successfully.'}, status=204)
            response.delete_cookie('jwt')
            return response
        else:
            return Response({'error': 'You cannot delete another user.'}, status=403)

# User LOGIN  
class UserLoginView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]
    
    def post(self, request):
        if request.COOKIES.get('jwt') is not None:
            return Response({"mssg": "Already Logged in"}, status=403)
             
            
        email = request.data['email']
        password = request.data['password']
        
        user = UserProfile.objects.filter(email=email).first()
        
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=401)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid Credentials'}, status=401)
        
        payload = {
            'id': user.id,
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'mssg': 'Successfully logged in'} 
        
        # return redirect('/api')
        return response
        

# EVENT VIEW SET
class EventViewSet(ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    

#RSVP VIEW SET
class RSVPViewSet(ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsRSVPUserOrReadOnly]
    
    @action(detail=True, methods=['get'], url_path='rsvp')
    def list_rsvps(self, request, pk=None):
        event = get_object_or_404(Events, pk=pk)
        rsvps = RSVP.objects.filter(event=event)
        serializer = RSVPSerializer(rsvps, many=True)
        if serializer.data == []:
            return Response({'mssg': "No RSVP's yet"})
        return Response(serializer.data)
    
    # POST /events/{event_id}/rsvp/
    @action(detail=True, methods=['post'], url_path='rsvp')
    def rsvp_to_event(self, request, pk=None):
        event = get_object_or_404(Events, pk=pk)
        user = request.user
        status = request.data.get('status')

        # Ensure user has not RSVP'd to the event already
        existing_rsvp = RSVP.objects.filter(user=user, event=event).first()
        if existing_rsvp:
            return Response({"mssg": "You have already RSVP'd to this event."}, status=400)

        # Create new RSVP
        rsvp = RSVP.objects.create(user=user, event=event, status=status)
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['get'], url_path='rsvp/(?P<user_id>[^/.]+)')
    def get_rsvp(self, request, pk=None, user_id=None):
        event = get_object_or_404(Events, pk=pk)
        user = get_object_or_404(UserProfile, pk=user_id)
        rsvp = get_object_or_404(RSVP, event=event, user=user)
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data)
    
    # PUT /events/{event_id}/rsvp/{user_id}/
    @action(detail=True, methods=['put'], url_path='rsvp/(?P<user_id>[^/.]+)')
    def update_rsvp(self, request, pk=None, user_id=None):
        
        # Update RSVP status for a specific user and event
        event = get_object_or_404(Events, pk=pk)
        user = get_object_or_404(UserProfile, pk=user_id)

        # Ensure the RSVP exists
        rsvp = get_object_or_404(RSVP, event=event, user=user)
        if user != self.request.user:
            return Response({"error": "You cannot update other's RSVP"}, status=403)
       
        status = request.data.get('status')

        # Update RSVP status
        rsvp.status = status
        rsvp.save()
        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data, status=200)
    
    # DELETE /events/{event_id}/rsvp/{user_id}/
    @action(detail=True, methods=['delete'], url_path='rsvp/(?P<user_id>[^/.]+)')
    def delete_rsvp(self, request, pk=None, user_id=None):
        event = get_object_or_404(Events, pk=pk)
        user = get_object_or_404(UserProfile, pk=user_id)

        # Ensure the RSVP exists
        rsvp = get_object_or_404(RSVP, event=event, user=user)
        if user != self.request.user:
            return Response({"error": "You cannot delete other's RSVP"}, status=403)
        rsvp.delete()
        return Response({'mssg': 'Successfully Deleted'}, status=204)