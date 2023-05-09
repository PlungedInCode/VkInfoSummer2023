from rest_framework import serializers
from .models import User, FriendRequest, Friendship

class UserSerializer(serializers.ModelSerializer):
    """id, username"""
    class Meta:
        model = User
        fields = ['id', 'username']

class FriendRequestSerializer(serializers.ModelSerializer):
    """sender, recipient, status"""
    class Meta:
        model = FriendRequest
        fields = '__all__'

class FriendshipSerializer(serializers.ModelSerializer):
    """user1 user2"""
    class Meta:
        model = Friendship
        fields = '__all__'
