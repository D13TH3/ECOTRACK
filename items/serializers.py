from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Item, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ItemSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    claimant = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'title', 'description', 'image', 'latitude', 'longitude',
            'address_hint', 'status', 'status_display', 'donor', 'claimant',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'donor', 'claimant', 'created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'item_title',
            'actor', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'notification_type', 'actor', 'created_at']
