# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from django.core.checks import messages
from channels.generic.websocket import WebsocketConsumer
from .models import ChatRoom
from django.contrib.auth.models import User
from .models import ChatMessage, ChatMessageManager

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        username = self.scope['user']
        user = User.objects.get(username=username)
        room_name = self.scope['url_route']['kwargs']['room_name']
        room = ChatRoom.objects.get(title=room_name)
        try:
            room.connect_user(user)
        except:
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': str(username) + ' has joined the chat',
            }
        )

        messages = ChatMessageManager().by_room(room)

        for m in messages[:3:-1]:
            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': str(m.content)
            }))


    def disconnect(self, close_code):
        username = self.scope['user']
        user = User.objects.get(username=username)
        room_name = self.scope['url_route']['kwargs']['room_name']

        ChatRoom.objects.get(title=room_name).disconnect_user(user)

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        username = self.scope['user']
        user = User.objects.get(username=username)

        room_name = self.scope['url_route']['kwargs']['room_name']
        room = ChatRoom.objects.get(title=room_name)

        ChatMessage(
            user = user,
            room = room,
            content = message,
        ).save()

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

