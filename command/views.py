# -*- coding: utf-8 -*-                        
from django.shortcuts import redirect, render_to_response 
from django.contrib.auth.models import User
from django.core.mail import send_mail
import datetime,re,json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext

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
        title = "激活失败" if info['language']=="zh-CN" else 'Activation failed'
        e_types = "用户名不存在" if info['language']=='zh-CN' else 'Username non-exist'
        e_content = "请重新注册。点击：" if info['language']=='zh-CN' else 'Please register again. '
        c_content += "<a href="/register/">Click</a>"
        e_additional = ""
        return return_page(request,
                           "bs_error.html",
                           title,
                           {'language':info['language'],
                            'username':param["name"],
                            'error_type': e_types,
                            'error_content':e_content,
                            'error_additional': e_additional})
        # return a page saying username does not exist, you need register again
        

commands_handler = {
    'activate_user':activate_user
    
}

def main(request):
    content = request.GET.get('content', '')
    if content != '':
        #activate the user
        link = json.loads(decrypt_string(content))
        return commands_handler[link["command"]](request, link)
        #return HttpResponse(decrypt_string(content) + "-->")
    else:
        return HttpResponse("no content fetched at all")
# request, 
# { 'language':info['language'],
#   'username':request.session["inactive_user"],
#   'link':link_text})

#     send_mail("hello from boxshell",content,'admin@boxshell.com',
#               ['spikey@nvidia.com'])

def send_activation_email(request,param):
    info = check_language(request)
    title = "Boxshell账号激活" if info['language']=="zh-CN" else 'Activation Account to Boxshell'
    content = ""
    sender = "admin@boxshell.com"

    try:
        user=User.objects.get(username=param["username"])
    except ObjectDoesNotExist:
        # return to error page
        title = "发送邮件失败" if info['language']=="zh-CN" else 'Send Activation mail failed'
        e_types = "用户名不存在" if info['language']=='zh-CN' else 'Username non-exist'
        e_content = "请重新注册。点击：" if info['language']=='zh-CN' else 'Please register again. '
        c_content += "<a href="/register/">Click</a>"
        e_additional = ""
        return return_page(request,
                           "bs_error.html",
                           title,
                           {'language':info['language'],
                            'username':param["username"],
                            'error_type': e_types,
                            'error_content':e_content,
                            'error_additional': e_additional})
    receiver = user.email
    send_mail(
        title,
        content,
        sender,
        receiver
    )
