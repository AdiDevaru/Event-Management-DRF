from rest_framework import serializers
from .models import Events, RSVP, Review, Invitations

from django.contrib.auth import get_user_model
UserProfile = get_user_model()

# UserProfile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'email', 'password', 'full_name', 'bio', 'location', 'profile_picture']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = UserProfile(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            bio=validated_data['bio'],
            location=validated_data['location'],
            profile_picture=validated_data['profile_picture']
        )
        user.set_password(validated_data['password'])  # Store hashed password 
        user.save()
        return user
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password']) # Store hased password
        
        # Update other fields as usual
        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance

# Events Serializer
class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField() # return __str__ method of UserProfile Model
    class Meta:
        model = Events      
        fields = '__all__'
        read_only_fields = ['organizer']
        
# RSVP Serializer
class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # return __str__ method of UserProfile Model
    event = serializers.StringRelatedField() # return __str__ method of Events Model
    class Meta:
        model = RSVP
        fields = '__all__'
        read_only_fields = ['user', 'event']

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # return __str__ method of UserProfile Model
    event = serializers.StringRelatedField() # return __str__ method of Events Model
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'event']
        
# Invitations Serializer
class InvitationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() # return __str__ method of UserProfile Model
    event = serializers.StringRelatedField() # return __str__ method of Events Model
    class Meta:
        model = Invitations
        fields = ['id', 'event', 'user']
        
class BulkInvitationSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())