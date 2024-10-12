SECRET_KEY = 'adidevaru$@9182'
import jwt

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.conf import settings
from django.contrib.auth import get_user_model

UserProfile = get_user_model()

#Custom Authentication Model
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('jwt')  
        if not token:
            return None

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        user = UserProfile.objects.filter(id=payload['id']).first()

        if not user:
            raise AuthenticationFailed('User not found')

        return (user, None)
