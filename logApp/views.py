from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from DjangoProject import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail.message import EmailMessage


# Create your views here.
def home(request):
    return render(request, 'logApp1/index.html')


def signup(request):
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists...! Please try some other Username or contact to SAMIR PADEKAR")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, 'Email is already in the use...! Please try other email address or contact to SAMIR PADEKAR')
            return redirect('home')

        if len(username)>30:
            messages.error(request,'Username should not be greater than 30 characters or contact to SAMIR PADEKAR')

        if pass1 != pass2 :
            messages.error(request, "your password doesn't match with above password or contact to SAMIR PADEKAR")

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric or contact to SAMIR PADEKAR")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request, 'Your account has been created succesfully,\n thank you...!!!\n we have sent you s confirmation email in orrder to activate ana ccount please check email \n or contact to Samir Padekar')


        website1 = 'welcome to JARVIS software stores...!!!'
        msg = "Hello " + myuser.first_name +  " !!!! \n" + " Welcone to Jarvis store  \n thank you for visiting our website \n we have sent you a confirmation email \n or contact to SAMIR PADEKAR \n please check your email to activate your account \n regards \n Samir Padekar"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(website1, msg, from_email, to_list, fail_silently=True)


        current_site = get_current_site(request)
        email_subject = "confirm your email at JARVIS - django login"
        msg2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            msg2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()


        return redirect('signin')

    return render(request , 'logApp1/signup.html')


def signin(request):#.
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username , password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'logApp1/index.html', {'fname':fname})

        else:
            messages.error(request,"Bad Credenrials...!!!")
            return redirect('home')
    return render(request , 'logApp1/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged-Out Succesfully....!!!" )
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)

    except (TypeError,ValueError, OverflowError, User.DoesNotExist):
        myuser = None



    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')