from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
import random

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class OTPCode(models.Model):
    email = models.OneToOneField(User,on_delete=models.CASCADE)
    generated_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        self.generated_otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.expires_at = self.otp_expiry  # ensure both fields are aligned
        self.save()
        self.send_otp_email()

    def send_otp_email(self):
        subject = 'Your OTP for Login'
        message = f'Hello,\n\nYour OTP for login is {self.  generated_otp}. It will expire in 5 minutes.'
        from_email = 'jhss12ahariharan@gmail.com'  # Replace with your email
        send_mail(subject, message, from_email, [self.email], fail_silently=False)

    def is_otp_valid(self, otp):
        return self.generated_otp == otp and self.otp_expiry and self.otp_expiry > timezone.now()

    def __str__(self):
        return f"{self.email} - {self.generated_otp}"
