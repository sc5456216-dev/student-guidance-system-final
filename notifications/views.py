from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import NotificationSettings
from .serializers import NotificationSettingsSerializer

class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get or create settings for the logged-in user
        settings, _ = NotificationSettings.objects.get_or_create(user=self.request.user)
        return settings