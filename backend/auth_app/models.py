from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

class User(AbstractUser):
    # Remove username field
    username = None
    
    # Primary key and required fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('email address', unique=True)
    name = models.CharField('full name', max_length=100)
    
    # Authentication fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional fields required
    
    # Custom fields
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']  # Or use email if preferred
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email