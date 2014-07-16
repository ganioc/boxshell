# -*- coding: utf-8 -*-                                                            

from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, Template
from django.template.loader import get_template
import datetime,re,json

################################################################################   
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
        temp = get_template('bs_register.html')

        html = temp.render(Context({
                    'title':title,
                    'language':info['language'],
                    'user':request.user}))
        
        return HttpResponse(html)

#show the terms
def terms(request):
    content ="<h1>你好！</h1><p>激活密码如下：</p>"
    send_mail("hello from boxshell",content,'admin@boxshell.com',
              ['spikey@nvidia.com'])

    info = check_language(request)
    title = "条款" if info['language']=="zh-CN" else 'Terms'

    temp = get_template('bs_terms.html')

    html = temp.render(Context({
                'title':title,
                'language':info['language'],
                'user':request.user}))

    return HttpResponse(html)



    



