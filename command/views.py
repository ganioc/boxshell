# -*- coding: utf-8 -*-                        
from django.shortcuts import redirect, render_to_response 
from django.contrib.auth.models import User
from django.core.mail import send_mail
import datetime,re,json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext, Context, Template
import smtplib

def transform_number(n):
    "input 32~126, output 32~126"
    temp_n = 126 - n + 32;
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

def error_page(request,username, e_types,e_content,e_additional):
    info = check_language(request)
    title = "错误" if info['language']=="zh-CN" else 'Error'
    return return_page(request,
                       "bs_error.html",
                       title,
                       {'language':info['language'],
                        'username':username,
                        'error_type': e_types,
                        'error_content':e_content,
                        'error_additional': e_additional})

def ok_page(request,username, e_types,e_content,e_additional):
    info = check_language(request)
    title = "成功" if info['language']=="zh-CN" else 'OK'
    return return_page(request,
                       "bs_ok.html",
                       title,
                       {'language':info['language'],
                        'username':username,
                        'ok_content':e_content,
                        'ok_additional': e_additional})

def nonexist_user_page(request, username):
    info = check_language(request)
    title = "用户名不存在" if info['language']=="zh-CN" else 'Username non exist'
    e_types = "用户名不存在" if info['language']=='zh-CN' else 'Username non-exist'
    e_content = "请重新注册。点击：" if info['language']=='zh-CN' else 'Please register again. '
    c_content += "<a href="/register/">Click</a>"
    e_additional = ""
    return return_page(request,
                       "bs_error.html",
                       title,
                       {'language':info['language'],
                        'username':username,
                        'error_type': e_types,
                        'error_content':e_content,
                        'error_additional': e_additional})

# Create your views here.

    # link = {"command":"activate_user",
    #         'name':request.session["inactive_user"],
    #         'date':datetime.datetime.strftime('%Y-%m-%d %H:%M:%S')
    # }
    # link_text= settings.SITE_URL + "command/" + "?content=" + encrypt_string(json.dumps(link))
# try:
#     e = Entry.objects.get(id=3)
#     b = Blog.objects.get(id=1)
# except ObjectDoesNotExist:
#     print("Either the entry or blog doesn't exist.")


def activate_user(request, param):
    info = check_language(request)

    try:
        user = User.objects.get( username=param["name"])
        user.is_active = True
        user.save()
        title = "激活成功" if info['language']=="zh-CN" else 'Activation succeed'
        # jump to a page, saying you have activated your account successfully
        return return_page(request,
                           "bs_activate_ok.html",
                           title,
                           {'language':info['language'],
                            'username':user.username})

    except ObjectDoesNotExist:
        return nonexist_user_page(request,param["username"])

# this is a function bundler
commands_handler = {
    'activate_user':activate_user
}

#the entry point for /command/ url
def main(request):
    content = request.GET.get('content', '')
    if content != '':
        #activate the user
        link = json.loads(decrypt_string(content))
        return commands_handler[link["command"]](request, link)
        #return HttpResponse(decrypt_string(content) + "-->")
    else:
        return HttpResponse("no content fetched at all")


def get_activation_message(param):
    message = ""
    if param["language"] == "zh-CN":
        message = "你好 {{ name }}:\n
        请点击以下链接来激活在Boxshell网的帐号。\n\n{{ link }}\n\n请勿回复本邮件。谢谢！\n\nBoxshell"
    else:#english
        message = "Hello Mr(Ms) {{ name }}:\n
        Please click below link to activate your account on Boxshell.\n\n {{ link }}\n\nPlease don't re this mail. Thanks!\n\nBoxshell"
    t = Template(message)
    c = Context({'name':param["username"],
                 'link':param["link"]})
    return t.render(c)

# info needed for send_mail 
# { 'language':info['language'],
#   'username':request.session["inactive_user"],
#   'link':link_text})

#     send_mail("hello from boxshell",content,'admin@boxshell.com',
#               ['spikey@nvidia.com'])

def send_activation_email(request,param):
    info = check_language(request)
    title = "Boxshell账号激活" if info['language']=="zh-CN" else 'Activation Account to Boxshell'
    content = get_activation_message(param)
    sender = "admin@boxshell.com"

    try:
        user=User.objects.get(username=param["username"])
    except ObjectDoesNotExist:
        # return to error page
        return nonexist_user_page(request,param["username"])

    receiver = user.email

    try:
        send_mail(
            title,
            content,
            sender,
            receiver
        )
    except  smtplib.SMTPException:
        if info['language']=="zh-CN":
            return error_page(request,param["username"],"邮件发送失败","由于故障问题 , 帐号激活邮件发送失败！", "")
        else:
            return error_page(request,param["username"],"Send mail failed","Something wrong , activation mail is not delivered","")

    return ok_page(request,param["username"],"邮件发送成功","请及时查看您的注册邮箱,尽快完成注册。")
