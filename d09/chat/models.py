from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class ChatMessageManager(models.Manager):
	def by_room(self, room):
		messages = ChatMessage.objects.filter(room=room).order_by("-created")
		return messages


class ChatRoom(models.Model):
	title = models.CharField(max_length=255, unique=True, blank=False)
	users = models.ManyToManyField(User, blank=True)

	def __str__(self):
		return self.title

	def connect_user(self, user):
		if not user in self.users.all():
			self.users.add(user)
			self.save()

	def disconnect_user(self, user):
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			return True
		return False


class ChatMessage(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
	content = models.TextField(unique=False, blank=False)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.content
