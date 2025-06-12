from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import OTPCode
from django.utils import timezone

def send_otp_view(request):
    email = request.GET.get('email')

    otp_instance = OTPCode.objects.create(email=email, expires_at=timezone.now())
    otp_instance.generate_otp()

    return JsonResponse({'message': 'OTP sent successfully.'})

def validate_otp_view(request):
    email = request.GET.get('email')
    otp = request.GET.get('otp')

    try:
        otp_instance = OTPCode.objects.filter(email=email).latest('created_at')
    except OTPCode.DoesNotExist:
        return JsonResponse({'message': 'OTP not found.'}, status=404)

    if otp_instance.is_otp_valid(otp):
        otp_instance.is_verified = True
        otp_instance.save()
        return JsonResponse({'message': 'OTP verified successfully.'})
    else:
        return JsonResponse({'message': 'Invalid or expired OTP.'}, status=400)

