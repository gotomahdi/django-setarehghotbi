from django.shortcuts import render , redirect 
from django.contrib.sites.shortcuts import get_current_site
from .forms import SignUpForm ,LoginForm ,PasswordRestFrom
from django.contrib.auth import authenticate ,login ,logout
from django.http import HttpResponse ,HttpResponseRedirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_str ,force_bytes
from django.utils.http import urlsafe_base64_decode ,urlsafe_base64_encode
from .models import User
from .tokens import account_activation_token
from django.db import IntegrityError


# Create your views here.



def Activate(request, uidb64, token):   
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token) and user.is_active != True:
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.save()
        return HttpResponseRedirect('account:login')
    else:
        return render(request, 'account/registration/activation_invalid.html')




def SignUpView(request):

    if request.method == 'POST':
        form=SignUpForm(request.POST or None)
        if form.is_valid():
            user=form.save()

            user.is_activate=False
            user.save()

            current_site=get_current_site(request)
            subject='Setarehghotbi Activation Account'

            message = render_to_string('account/registration/activation_request.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })

            user.email_user(subject,message)
            messages.success(request,'پیامی حاوی لینک اهراز حویت به ایمیل شما ارسال شد.')
            return render(request,'account/registration/sign_up.html',{'form':form})
        else:
            return render(request,'account/registration/sign_up.html',{'form':form})
    else:
        form=SignUpForm()

    return render(request,'account/registration/sign_up.html',{'form':form})




def LoginView(request):

    if request.method == 'POST':
        form=LoginForm(request.POST or None)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            username = form.cleaned_data.get('username')
            user=authenticate(request,username=username,password=password)
            if user:
                login(request,user)
                return redirect('blog:home')
            else:
                messages.error(request,'نام کاربری و یا رمز عبور صحیح نمی باشد')
                return render(request,'account/registration/login.html',{'form':form})
        else:
            return render(request,'account/registration/login.html',{'form':form})
    else:
        form=LoginForm()

    return render(request,'account/registration/login.html',{'form':form})





def LogoutView(request):

    logout(request)
    return redirect('blog:home')






def ResetPasswordView(request):

    if request.method=='POST':
        email=request.POST.get('email')
        try:
            user=User.objects.get(email=email)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None:
            current_site=get_current_site(request)
            subject='Setarehghotbi Rest Password'

            message = render_to_string('account/registration/activation_request_rest_password.html',{
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })

            user.email_user(subject,message)
            messages.success(request,'پیامی حاوی لینک تغییر گذرواژه به ایمیل شما ارسال شد.')
            return render(request,'account/registration/rest_password_email.html')
        else:
            messages.error(request,'فردی با ایمیل وارد شده در سایت موجود نمی باشد')
            return render(request,'account/registration/rest_password_email.html')            

    else:
        return render(request,'account/registration/rest_password_email.html')






def ResetPasswordActivate(request, uidb64, token):   
    if request.method=='POST':

        form=PasswordRestFrom(request.POST or None)
        if form.is_valid():
                try:
                    uid = force_str(urlsafe_base64_decode(uidb64))
                    user = User.objects.get(pk=uid)
                except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                    user = None
                # checking if the user exists, if the token is valid.
                if user is not None and account_activation_token.check_token(user, token):

                    form_data=form.cleaned_data
                    # check passwords for rest password user
                    if form_data['password1'] == form_data['password2']:
                        #Password reset and password change link expiration
                        user.set_password(form_data['password1'])
                        user.save()
                        return redirect('account:login')
                    else:
                        # show error if not set passwords
                        messages.error(request,'گذرواژه ها یکسان نیستند')
                        return render(request,'account/registration/rest_password_confirm.html',{'form':form})
                else:
                    return render(request, 'account/registration/activation_invalid.html')
        else:
            return render(request,'account/registration/rest_password_confirm.html',{'form':form})
            form=PasswordRestFrom()

        return render(request,'account/registration/rest_password_confirm.html',{'form':form})
    else:
        return render(request, 'account/registration/activation_invalid.html')
