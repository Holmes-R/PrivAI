from django.db import models

# Create your models here.
from auth_app.models import User

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=50)  # manual, gdocx, notion
    file_type = models.CharField(max_length=10)  # pdf, txt, docs
    created_at = models.DateTimeField(auto_now_add=True)
