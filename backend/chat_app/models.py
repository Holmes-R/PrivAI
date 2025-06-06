from django.db import models

# Create your models here.
from auth_app.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)  # user / assistant
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
