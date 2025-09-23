from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Conversation(TimeStampedModel):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")

    def __str__(self):
        return f"Conversation {self.id}"


class Message(TimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.conversation.id}"
