import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification, Dashboard

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email):
    """Generate and send OTP to the user's email"""
    otp_code = generate_otp()
    
    # Delete any existing unverified OTPs for this email
    OTPVerification.objects.filter(email=email, is_verified=False).delete()
    
    # Create new OTP record
    otp_record = OTPVerification.objects.create(
        email=email,
        otp_code=otp_code
    )
    
    # Send OTP via email
    subject = 'Login Verification Code'
    message = f'''
    Hello,
    
    Your login verification code is: {otp_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    Website Builder Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    return otp_record

def verify_otp_code(email, otp_code):
    """Verify the OTP code for the given email"""
    try:
        otp_record = OTPVerification.objects.get(
            email=email,
            otp_code=otp_code,
            is_verified=False
        )
        
        if otp_record.is_expired():
            return False
        
        # Mark as verified
        otp_record.is_verified = True
        otp_record.save()
        return True
    except OTPVerification.DoesNotExist:
        return False