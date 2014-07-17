# -*- coding: utf-8 -*-                                                            
from django.shortcuts import redirect, render_to_response 
from django.template import RequestContext
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, Template
from django.template.loader import get_template
import datetime,re,json
from django.conf import settings

################################################################################
def transform_number(n):
    "input 33~126, output 33~126"
    temp_n = 126 - n + 33;
    return temp_n;

def detransform_number(n):
    "reverse of transform_number"
    return transform_number(n)

def encrypt_character(c):
    "To encrypt a character to another one in 0~255"
    temp_c = ord(c)
    temp_c = transform_number(temp_c);
    return chr(temp_c)

def decrypt_character(c):
    "To decrypt a character to the correct one"
    temp_c = ord(c)
    temp_c = detransform_number(temp_c);
    return chr(temp_c)

def encrypt_string(s):
    str = ""
    for i in s:
        str = str + encrypt_character(i)
    return str

def decrypt_string(s):
    str = ""
    for i in s:
        str = str + decrypt_character(i)
    return str
   
def is_zh_language(request):
    lang = request.META['HTTP_ACCEPT_LANGUAGE'].split(',')
    return True if (("zh" in lang) or ("zh-cn" in lang) or ("zh-CN" in lang)) else\
 False

#check language                                                                    
def check_language(request):
    if "lang" not in request.session:
	request.session["lang"] = "zh-CN" if is_zh_language(request) else "en-US"

    lan = "zh-CN" if request.session["lang"] == "zh-CN" else "en-US"
    output = {}
    output['language'] = lan
    return output

def return_page(request, template_file,title, dictionary):
    diction = {'title':title,'language':request.session["lang"]}
    diction.update(dictionary)
    return render_to_response(template_file,diction,context_instance=RequestContext(request))


# class MyRegistrationForm(UserCreationForm):
#     pass

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

    temp = get_template('bs_main.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)


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
    title = "登录" if info['language']=="zh-CN" else 'Login'

    temp = get_template('bs_signin.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)

def register(request):
    info = check_language(request)

    if request.method == "POST":
        pass
        
    else:

        title = "注册" if info['language']=="zh-CN" else 'Register'
        return return_page(request,'bs_register.html',title,{
            'language':info['language'],
            'user':request.user}
        )

#show the terms
def terms(request):
    # if settings.SITE_URL == "http://www.boxshell.com/":
    #     content ="<h1>你好！</h1><p>激活密码如下：</p>"
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



    



