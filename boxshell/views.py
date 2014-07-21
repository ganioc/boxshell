# -*- coding: utf-8 -*-                        
from django.http import HttpResponseRedirect                                    
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, Template
from django.template.loader import get_template
import datetime,re,json, urllib
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from command.views import send_activation_email,encrypt_string,return_page, check_language, b_exist_email
################################################################################
   
#form for signin
class MySigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(render_value=False))
    def clean_email(self):
        try:
            User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError("This email is not existed")
        return self.cleaned_data['email']
    def clean_password(self):
        return self.cleaned_data['password']
    def clean(self):
        return self.cleaned_data
    def save(self):
        return {'email':self.cleaned_data['email'],
                'password':self.cleaned_data['password']}

# form for registration
class MyRegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(render_value=False))

    def clean_username(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("This username is already in use.➥Please choose another.")

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("You must type the same➥password each time")
            return self.cleaned_data
            
    def save(self):
        new_user = User.objects.create_user(
            username = self.cleaned_data['username'],
            email = self.cleaned_data['email'],
            password = self.cleaned_data['password1']
            )
        new_user.is_active = False
        new_user.save()
        return new_user

#################################################################################  
#only for language function, only support chinese and english                      
def switch_language(request):
    if request.method == "GET":
	lang = request.GET["language"]
	if lang == "english":
            request.session["lang"] = "en-US"
	else:
            request.session["lang"] = "zh-CN"
	message = {'change':"succeed"}
	return HttpResponse(json.dumps(message),content_type="application/json")

#main entry point for site                                                         
#need to handle user login information                                             
def home(request):
    info = check_language(request)
    title = "主页" if info['language']=="zh-CN" else 'Home'

    return return_page(request,'bs_main.html',
                       title,
                       {'language':info['language'],
                        'user':request.user})


def about(request):
    info = check_language(request)
    title = "关于" if info['language']=="zh-CN" else 'About'

    temp = get_template('bs_about.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)

def contact(request):
    info = check_language(request)
    title = "联系" if info['language']=="zh-CN" else 'Contact'

    temp = get_template('bs_contact.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)


def signin(request):
    info = check_language(request)
    title = "登录" if info['language']=="zh-CN" else 'Signin'
    if request.method == "POST":
        form = MySigninForm(data = request.POST)
        if form.is_valid():
            temp_user = form.save()
            #check if email and password match
            myuser=User.objects.get(email=temp_user['email'])
            user = auth.authenticate(username=myuser.username,password=temp_user['password'])
            if user is not None and user.is_active:
                auth.login(request,user)
                return HttpResponseRedirect("/")
            elif user is not None and not  user.is_active:
                form = {'activation':{'errors':True}}
            else:
                form = {'password':{'errors':True}}
    else:
        form= MySigninForm()

    return return_page(request,'bs_signin.html',
                       title,
                       {'language':info['language'],
                        'form':form})
def register(request):
    info = check_language(request)
    title = "注册" if info['language']=="zh-CN" else 'Register'

    if request.method == "POST":
        form = MyRegistrationForm(data = request.POST)
        if form.is_valid():
            new_user = form.save()
            request.session["inactive_user"] = new_user.username
            #if new_user.username,(no need )
            #only check email exist
            #User can register multiple account using one email address, no he can't!
            if b_exist_email(new_user.email):
                form = {'email':{'errors':True}}
                return return_page(request,'bs_register.html',title,{
                        'language':info['language'],
                        'form':form})
            return HttpResponseRedirect("/activate/")
    else:
        form = MyRegistrationForm()
    
    return return_page(request,'bs_register.html',title,{
        'language':info['language'],
        'form':form})


#show the terms
def terms(request):
    # if settings.SITE_URL == "http://www.boxshell.com/":
    #     content ="<h1>“你好”</h1><p>激活密码如下：</p>"
    #     send_mail("hello from boxshell",content,'admin@boxshell.com',
    #               ['spikey@nvidia.com'])
    # else:
    #     pass
        # give you a link to activate the user

    info = check_language(request)
    title = "条款" if info['language']=="zh-CN" else 'Terms'
    
    temp = get_template('bs_terms.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)

#Activate your account after registration
def activate(request):
    info = check_language(request)
    title = "激活账号" if info['language']=="zh-CN" else 'Activate Account'
    
    link = {"command":"activate_user",
            'name':request.session["inactive_user"],
            'date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    link_text= settings.SITE_URL + "command/" + "?content=" + urllib.quote(encrypt_string(json.dumps(link)))
            
    if settings.SITE_URL == "http://127.0.0.1:8000/":
        return return_page(request,'bs_activate.html',
                           title,
                           { 'language':info['language'],
                             'username':request.session["inactive_user"],
                             'link':link_text})
    else:
        return send_activation_email(
            request, 
            { 'language':info['language'],
              'username':request.session["inactive_user"],
              'link':link_text})
        # send a mail containing the activation link inside
        


        
def account(request):
    info = check_language(request)
    title = "账户" if info['language']=="zh-CN" else 'Account'

    return return_page(request,'bs_account.html',
                       title,
                       {'language':info['language'],
                        'user':request.user})

def signout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
