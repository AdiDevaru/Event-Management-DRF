# from django.shortcuts import redirect
SECRET_KEY = 'adidevaru$@9182'

from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import permissions

from .models import Events
from .serializers import UserProfileSerializer, EventSerializer
from .permissions import IsOwnerOrReadOnly, IsOrganizerOrReadOnly

from django.contrib.auth import get_user_model
UserProfile = get_user_model()
import jwt
# from pprint import pprint

# USER VIEW SET
class UserProfileViews(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    #Allow non-authenticated users to create a new UserProfile 
    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]  
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        #Logged in users cannot create a new UserProfile
        if request.user.is_authenticated:
            return Response({'detail': 'Logged in users cannot create a new profile.'}, status=403)
        
        #Automatically LOGIN new user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        payload = {'id': user.id}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'mssg': 'Successfully logged in'} 
        
        return response
    
    #Delete LOGIN token when user is deleted     
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance == request.user:
            self.perform_destroy(instance)
            response = Response({'detail': 'User deleted successfully.'}, status=204)
            response.delete_cookie('jwt')
            return response
        else:
            return Response({'detail': 'You cannot delete another user.'}, status=403)

#User LOGIN  
class UserLoginView(APIView):
    authentication_classes = []  
    permission_classes = [AllowAny]
    
    def post(self, request):
        if request.COOKIES.get('jwt') is not None:
            response = Response({"mssg": "Already Logged in"}, status=403)
            return response
            
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
        
        return response
        # return redirect('/api')
        

#EVENT VIEW SET
class EventViewSet(ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    