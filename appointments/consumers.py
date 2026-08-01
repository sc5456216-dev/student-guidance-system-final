import json
import urllib.parse
import traceback
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            print("🔵 Full consumer connect() called")
            query_string = self.scope['query_string'].decode()
            print(f"🔍 Query string: {query_string}")

            params = urllib.parse.parse_qs(query_string)
            token_list = params.get('token', [])
            if not token_list:
                print("❌ No token provided – closing")
                await self.close()
                return

            token_str = token_list[0].strip()
            print(f"🔑 Token: {token_str[:30]}...")

            user = await self.get_user_from_token(token_str)
            print(f"👤 User: {user} (authenticated: {user.is_authenticated if user else False})")

            if user and user.is_authenticated:
                self.user = user
                self.room_group_name = f'user_{user.id}'
                # Try to add to group – if this fails, we'll see the error
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                print(f"✅ WebSocket accepted for user {user.email}")
            else:
                print("❌ Authentication failed – closing")
                await self.close()

        except Exception as e:
            print("=" * 60)
            print("🔥 CONSUMER ERROR:")
            traceback.print_exc()
            print("=" * 60)
            await self.close()

    async def disconnect(self, close_code):
        print(f"🔌 Disconnected (code: {close_code})")
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        print(f"📩 Received: {text_data}")
        # Optionally handle incoming messages

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'appointment_id': event.get('appointment_id'),
            'status': event.get('status'),
        }))

    @database_sync_to_async
    def get_user_from_token(self, token_str):
        from rest_framework_simplejwt.tokens import AccessToken
        try:
            access_token = AccessToken(token_str)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            print(f"🔓 Token decoded for user {user.email}")
            return user
        except Exception as e:
            print(f"❌ Token decode error: {e}")
            return AnonymousUser()