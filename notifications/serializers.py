from rest_framework import serializers
from .models import NotificationSettings

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['email_notifications', 'in_app_notifications', 'updated_at']
        read_only_fields = ['updated_at']