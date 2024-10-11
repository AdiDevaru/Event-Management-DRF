from rest_framework import serializers
from .models import Events

from django.contrib.auth import get_user_model
UserProfile = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'password', 'full_name', 'bio', 'location', 'profile_picture']

    def create(self, validated_data):
        user = UserProfile(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        # Update other fields as usual
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)

        # Save the updated user
        instance.save()
        return instance
    
class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField()
    class Meta:
        model = Events      
        fields = '__all__'