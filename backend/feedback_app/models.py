from django.db import models

# Create your models here.
from auth_app.models import User
from chat_app.models import ChatSession

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
