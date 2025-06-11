from django.shortcuts import render
from django.http import JsonResponse
from .models import User,OTPCode
from django.utils import timezone
# Create your views here.


def request_otp(request):
    if request.method =='POST':
        email = request.POST.get('email')
        name = request.POST.get('name', 'New User')  # fallback if name not provided

        # 1. Get or create the user
        user, created = User.objects.get_or_create(email=email, defaults={'name': name})
        
        # 2. Get or create the OTPCode
        otp_obj, _ = OTPCode.objects.get_or_create(email=user)
        otp_obj.generate_otp()  # generates OTP, sets expiry, sends email

        return JsonResponse({'message': 'OTP sent to your email.'}, status=200)