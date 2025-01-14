import pyotp
import qrcode
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import json

def init_db():
    # Note: Django handles database initialization through models.py
    pass

@csrf_exempt
def enable_2fa(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not logged in'}, status=401)
    
    email = request.user.email
    secret = pyotp.random_base32()
    
    # Update user's 2FA settings in Django model
    user_profile = request.user.profile  # Assuming you have a profile model
    user_profile.secret_key = secret
    user_profile.is_2fa_enabled = True
    user_profile.save()
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(email, issuer_name="BPA Website")
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image.save(f"static/qr_codes/{email}_qr.png")
    
    return JsonResponse({
        'success': True,
        'qr_code_url': f"/static/qr_codes/{email}_qr.png",
        'secret': secret
    })

@csrf_exempt
def verify_2fa(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
        
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({'error': 'Missing verification code'}, status=400)

        # Get the stored code from session
        stored_data = request.session.get('2fa_code')
        if not stored_data:
            return JsonResponse({'error': 'No verification code found'}, status=400)

        stored_code = stored_data['code']
        expiry = datetime.fromisoformat(stored_data['expires'])

        # Check if code has expired
        if datetime.now() > expiry:
            del request.session['2fa_code']
            return JsonResponse({'error': 'Verification code has expired'}, status=400)

        # Verify the code
        if token == stored_code:
            # Clear the code from session after successful verification
            del request.session['2fa_code']
            return JsonResponse({'success': True, 'message': 'Verification successful'})
        else:
            return JsonResponse({'error': 'Invalid verification code'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def send_2fa_email(request):
    data = json.loads(request.body)
    email = data.get('email')
    
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    # Generate a 6-digit code
    code = pyotp.TOTP('').now()
    
    # Store the code in session
    request.session['2fa_code'] = {
        'code': code,
        'expires': str(datetime.now() + timedelta(minutes=5))
    }
    
    # Send email using Django's send_mail
    try:
        send_mail(
            'Your 2FA Code',
            f'Your 2FA verification code is: {code}\nThis code will expire in 5 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': '2FA code sent successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def reset_password(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email')
        new_password = data.get('new_password')
        
        if not email or not new_password:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Update password in your database here
        # ... (implement password update logic)

        return JsonResponse({'success': True, 'message': 'Password updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def forgot_password_screen(request):
    return render(request, 'forgot_screen/forgot_screen.html')

def code_verification_screen(request):
    return render(request, 'code_screen/code_screen.html')

def new_password_screen(request):
    return render(request, 'new_password/enter_new_password_screen.html')

def thank_you_screen(request):
    return render(request, 'forgot_password/thank_you_screen.html')

def test_page(request):
    return render(request, 'test_login.html')

@csrf_exempt
def test_reset_flow(request):
    if request.method == 'POST':
        try:
            # Simulate sending email
            code = '123456'  # Test code
            request.session['2fa_code'] = {
                'code': code,
                'expires': str(datetime.now() + timedelta(minutes=5))
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Test flow initialized',
                'test_code': code  # Only for testing!
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
