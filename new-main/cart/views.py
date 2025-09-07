from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_str
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout
from django.contrib.sites.shortcuts import get_current_site
import threading

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()

def send_activation_email(request, user, to_email):
    current_site = get_current_site(request)
    email_subject = "Activate your TruckBrand Account"
    email_body = render_to_string('activate.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email]
    )
    email.content_subtype = "html"  # Set the email content type to HTML
    
    # Send email in background
    EmailThread(email).start()

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        # Validate passwords
        if password != confirm_password:
            messages.warning(request, "Passwords do not match")
            return render(request, 'signup.html')

        # Check if user already exists
        try:
            if User.objects.filter(email=email).exists():
                messages.warning(request, "Email is already registered")
                return render(request, 'signup.html')

            # Create new user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = False
            user.save()

            # Send activation email
            try:
                send_activation_email(request, user, email)
                messages.success(request, "Please check your email to activate your account")
                return redirect('/cart/login/')
            except Exception as e:
                # If email sending fails, delete the user and show error
                user.delete()
                messages.error(request, "Could not send activation email. Please try again.")
                return render(request, 'signup.html')

        except Exception as e:
            messages.error(request, "An error occurred during registration")
            return render(request, 'signup.html')

    return render(request, 'signup.html')
  
class ActivateAccountView(View):
  def get(self,request,uidb64,token):
      try:
          uid=force_str(urlsafe_base64_decode(uidb64))
          user=User.objects.get(pk=uid)
      except Exception as identifier:
        user= None
      if user is not None and generate_token.check_token(user,token):
        user.is_active=True
        user.save()
        messages.info(request,"Account Activated Successfully")
        return redirect('/cart/login')
      return render(request,'activatefail.html') 
        
    


def handlelogin(request):
    if request.method=="POST":
        
        username=request.POST['email']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)
        
        if myuser is not None:
            login(request,myuser)
            messages.success(request,"login Success")
            return redirect('/') 
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/cart/login')
   
    return render(request,"login.html")
     
     
     
     
def handlelogout(request):
    logout(request)
    messages.info(request,"logout Success")
    return redirect('/cart/login')

class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)

        if user.exists():
            # current_site=get_current_site(request)
            email_subject='[Reset Your Password]'
            message=render_to_string('reset-user-password.html',{
                'domain':'127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token':PasswordResetTokenGenerator().make_token(user[0])
            })

            # email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            # email_message.send()

            messages.info(request,f"Check Your Email " )
            return render(request,'request-reset-email.html')

class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode the uidb64 to get user id
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Verify token
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, "Password reset link is invalid or has expired")
                return redirect('request-reset-email')
            
            # If token is valid, show reset password form
            context = {
                'uidb64': uidb64,
                'token': token,
            }
            return render(request, 'set-new-password.html', context)
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, "Invalid reset link")
            return redirect('request-reset-email')

    def post(self, request, uidb64, token):
        try:
            # Decode the uidb64 to get user id
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Get passwords from form
            password = request.POST.get('pass1')
            confirm_password = request.POST.get('pass2')
            
            # Validate passwords
            if not password or not confirm_password:
                messages.error(request, "Please enter both passwords")
                return render(request, 'set-new-password.html', {'uidb64': uidb64, 'token': token})
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match")
                return render(request, 'set-new-password.html', {'uidb64': uidb64, 'token': token})
            
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long")
                return render(request, 'set-new-password.html', {'uidb64': uidb64, 'token': token})
            
            # Set new password
            user.set_password(password)
            user.save()
            
            messages.success(request, "Password has been reset successfully! You can now login with your new password.")
            return redirect('/cart/login/')
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('request-reset-email')
            
