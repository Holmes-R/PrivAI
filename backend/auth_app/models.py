# auth_app/models.py

from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
import uuid
import random
from datetime import timedelta

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class OTPCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    otp = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.email}"

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=5)
        self.save()
        self.send_otp_email()

    def send_otp_email(self):
        subject = 'Your OTP for Verification'
        message = f'Your OTP is {self.otp}. It will expire in 5 minutes.'
        from_email = 'jhss12ahariharan@gmail.com'  # Replace with your verified sender
        send_mail(subject, message, from_email, [self.email], fail_silently=False)

    def is_otp_valid(self, input_otp):
        return (
            self.otp == input_otp
            and self.expires_at > timezone.now()
            and not self.is_verified
        )
