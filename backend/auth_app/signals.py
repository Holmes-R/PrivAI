from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, OTPCode

@receiver(post_save, sender=User)
def create_otp_code(sender, instance, created, **kwargs):
    if created:
        OTPCode.objects.create(email=instance)
