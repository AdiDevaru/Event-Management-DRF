SECRET_KEY = 'adidevaru$@9182'
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
# from pprint import pprint

from rest_framework.viewsets import  ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action

from .models import Events, RSVP, Review, Invitations
from .serializers import UserProfileSerializer, EventSerializer, RSVPSerializer, ReviewSerializer, InvitationSerializer, BulkInvitationSerializer
from .permissions import IsUserOrReadOnly, IsOrganizerOrReadOnly, IsOwnerOrReadOnly, IsEventOrganizerInvitation
# , IsInvited

from django.contrib.auth import get_user_model
UserProfile = get_user_model()
import jwt
 
 
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
        response = Response({'mssg': 'Successfully logged in'}, status=201)
        response.set_cookie(key='jwt', value=token, httponly=True)
        
        return response
    
    # Delete LOGIN token when user is deleted     
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance == request.user:
            self.perform_destroy(instance)
            response = Response({'detail': 'User deleted successfully.'}, status=204)
            response.delete_cookie('jwt')
            return response
        
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
        
        if not user or not user.check_password(password):
            return Response({'error': 'Invalid Credentials'}, status=401)
        
        # JWT Authentication
        payload = {
            'id': user.id,
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        response = Response({'mssg': 'Successfully logged in'}, status=200)
        response.set_cookie(key='jwt', value=token, httponly=True) 
        
        # return redirect('/api')
        return response
        

# EVENTS VIEW SET
class EventViewSet(ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]
                    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(organizer=self.request.user)
        
        if event.is_public:
            return Response(serializer.data, status=201)
        
        invitation_url = f'/api/events/{event.id}/invitations'
        return redirect(invitation_url)
        return Response({
            'mssg': 'Succesfully created a private event',
            'redirect_url': invitation_url,
        }, status=201)

# RSVP VIEW SET
class RSVPViewSet(ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    # GET /events/{event_id}/rsvp/
    @action(detail=False, methods=['get'], url_path='rsvp')
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
 
 
    # GET /events/{event_id}/rsvp/{user_id}/
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


# REVIEW VIEW SET
class ReviewViewSet(ModelViewSet):
    queryset = Review
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    # GET /events/{event_id}/reviews/
    @action(detail=False, methods=['get'], url_path='reviews')
    def get_review(self, request, pk):
        event = get_object_or_404(Events, pk=pk)
        reviews = Review.objects.filter(event=event)
        serializer = ReviewSerializer(reviews, many=True)
        if serializer.data == []:
            return Response({'mssg': "No Comments's yet"})
        return Response(serializer.data)
    
    # POST /events/{event_id}/reviews/
    @action(detail=True, methods=['post'], url_path='reviews')
    def post_review(self, request, pk):
        event = get_object_or_404(Events, pk=pk)
        user = request.user
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        
        existing_review = Review.objects.filter(user=user, event=event).first()
        if existing_review:
            return Response({"mssg": "You have already commented on this event."}, status=400)
        
        try:
            review = Review.objects.create(event=event, user=user, rating=rating, comment=comment)
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=201)
        except:
            return Response({'error': "Please enter valid details"})
            
    
    # GET /events/{event_id}/reviews/{user_id}/
    @action(detail=True, methods=['get'], url_path='reviews/(?P<review_id>[^/.]+)')
    def get_review_details(self, request, pk=None, review_id=None):
        event = get_object_or_404(Events, pk=pk)
        reviews = get_object_or_404(Review, pk=review_id)
        
        serializer = ReviewSerializer(reviews)
        return Response(serializer.data)
    
    # PUT /events/{event_id}/reviews/{user_id}/
    @action(detail=True, methods=['put'], url_path='reviews/(?P<review_id>[^/.]+)')
    def update_review(self, request, pk=None, review_id=None):
        event = get_object_or_404(Events, pk=pk)
        review = get_object_or_404(Review, pk=review_id)
        user = review.user

        if user != self.request.user:
            return Response({"error": "You cannot update other's Review"}, status=403)
       
        rating = request.data.get('rating')
        comment = request.data.get('comment')

        # Update REVIEW status
        try:
            review.rating = rating
            review.comment = comment
            review.save()
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=200)
        except:
            return Response({'error': "Please enter valid details"})
            
    # DELETE /events/{event_id}/reviews/{user_id}/
    @action(detail=True, methods=['delete'], url_path='reviews/(?P<review_id>[^/.]+)')
    def delete_review(self, request, pk=None, review_id=None):
        event = get_object_or_404(Events, pk=pk)
        review = get_object_or_404(Review, pk=review_id)
        user = review.user
        
        if user != self.request.user:
            return Response({"error": "You cannot delete other's Review"}, status=403)
        review.delete()
        return Response({'mssg': 'Successfully Deleted'}, status=204)
    

# INVITATIONS VIEW SET
class InvitationViewSet(ModelViewSet):
    queryset = Invitations.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsEventOrganizerInvitation]
    
    @action(detail=False, methods=['get'], url_path='invitations')
    def get_invitations(self, request, pk=None):
        event = get_object_or_404(Events, pk=pk)
        
        if event.is_public:
            return Response({'mssg': "No invitations for public event"}, status=400)
        
        if event.organizer != request.user:
            return Response({'error': "Cannot view this"}, status=403)
        
        invitations = Invitations.objects.filter(event=event)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='invitations')
    def post_invitations(self, request, pk=None):
        event = get_object_or_404(Events, pk=pk)
        
        if event.is_public:
            return Response({'error': "Cannot create invitations for public events"}, status=403)
        
        if event.organizer != request.user:
             return Response({"error": "Only organizer can make invitations"}, status=403)
        
        serializer = BulkInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.validated_data['user_ids']
        
        invitation_list = []
        for id in user_ids:
            user = get_object_or_404(UserProfile, pk=id)
            invitation = Invitations.objects.create(event=event, user=user)
            invitation_list.append(invitation)
        
        invitation_serializer = InvitationSerializer(invitation_list, many=True)
        return Response(invitation_serializer.data, status=201)
    
    @action(detail=True, methods=['get'], url_path='invitations/(?P<invitation_id>[^/.]+)')
    def get_invitation_details(self, request, pk=None, invitation_id=None):
        event = get_object_or_404(Events, pk=pk)
        
        if event.organizer != request.user:
            return Response({"error": "You cannot view invitations"}, status=403)
        
        invitation = get_object_or_404(Invitations, pk=invitation_id)
        
        serializer = InvitationSerializer(invitation)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='invitations/(?P<invitation_id>[^/.]+)')
    def delete_invitation(self, request, pk=None, invitation_id=None):
        event = get_object_or_404(Events, pk=pk)
        invitation = get_object_or_404(Invitations, pk=invitation_id)
        
        if event.organizer != self.request.user:
            return Response({"error": "You cannot delete invitations"}, status=403)
        invitation.delete()
        return Response({'mssg': 'Successfully Deleted'}, status=204)