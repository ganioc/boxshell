# -*- coding: utf-8 -*-                        
from django.shortcuts import redirect, render_to_response 
from django.contrib.auth.models import User
from django.core.mail import send_mail
import datetime,re,json, time
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.template import RequestContext, Context, Template,loader
import smtplib,os
from boxshell.settings import USER_FILE_ROOT
from django.core.files import File
from command.models import Account, Project

#this is a decorator function to make sure the user has logged in
def need_login(function):
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            return function(request, *args, **kw)
        else:
            return HttpResponseRedirect('/')
    return wrapper


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

def ok_page(request,username,e_content,e_additional):
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
        #clear account using the same email address
        clear_exist_email(user.email)

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
        if info['language']=="zh-CN":
            return error_page(request,"",u"无效链接",u"由于不明问题 , 该帐号激活链接是无效的！", "")
        else:
            return error_page(request,"",u"Invalid link",u"Something wrong , this link for activation account invalid.","")


def get_activation_message(param):
    message = ""
    if param["language"] == "zh-CN":
        message = u"你好 {{ name }}:\n请点击以下链接来激活在Boxshell网的帐号。\n\n{{ link }}\n\n请勿回复本邮件。谢谢！\n\nBoxshell"
    else:#english
        message = u"Hello Mr(Ms) {{ name }}:\nPlease click below link to activate your account on Boxshell.\n\n {{ link }}\n\nPlease don't re this mail. Thanks!\n\nBoxshell"
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
    title = u"Boxshell账号激活" if info['language']=="zh-CN" else u'Activation Account to Boxshell'
    content = get_activation_message(param)
    sender = "admin@boxshell.com"
    user = ""

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
            [receiver]
        )
    except  smtplib.SMTPException:
        if info['language']=="zh-CN":
            return error_page(request,param["username"],u"邮件发送失败",u"由于故障问题 , 帐号激活邮件发送失败！", "")
        else:
            return error_page(request,param["username"],u"Send mail failed",u"Something wrong , activation mail is not delivered","")

    if info['language']=="zh-CN":
        return ok_page(request,param["username"],u"邮件发送成功",u"请及时查看您的注册邮箱%s,尽快完成注册。" % user.email)
    else:
        return ok_page(request,param["username"],u"Email sending succeed.",u"Please check your mailbox %s, and finish the activation process." % user.email)


def b_exist_email(mail):
    user = User.objects.filter(email=mail,is_active=True)
    if user.exists():
        return True
    else:
        return False

def clear_exist_email(mail):
    users = User.objects.filter(email=mail,is_active=False)
    for i in users:
        i.delete()

def file_create_a_hello():
    with open(USER_FILE_ROOT + 'hello.world', 'w') as f:
        myfile = File(f)
        myfile.write('Hello World')
    f.closed

def file_check_exist(name):
    return os.path.isfile(name)

def file_create_dir(name):
    os.mkdir(name)

def file_create_file(name, content):
    fp = open(name,"w")
    fp.write(content)
    fp.close()
def file_delete_file(direc,name):
    os.chdir(direc)
    os.remove(name)

def file_delete_directory(direc):
    os.rmdir(direct)

def file_valid(name):
    if name[0] == '.':
        return False
    elif re.search(r".+[.]info" , name):
        return False
    return True

def file_read_file(name):
    pass
def file_list_file(directory):
    files =  os.listdir(directory)
    feedback = []
    os.chdir(directory)
    for file1 in files:
        if file_valid(file1):
            info = os.stat(file1)
            other_info = file_file_type(directory, file1 + '.info')
            temp = {}
            temp["name"] = file1
            temp["modified_datetime"] = "%s" % time.ctime(info.st_mtime)
            temp["type"] = other_info["type"]
            temp["description"] = other_info["description"]
            temp["size"] = info.st_size
            feedback.append(temp)

    return feedback

def file_write_file(str):
    pass

def file_copy_file(name,dest_dir):
    pass

def file_file_type(directory,filename):
    # judge a file type by is postfix name
    fp = open(directory + '/' + filename, "r")
    content = fp.read()
    fp.close()
    obj = json.loads(content)
    return obj

def return_user_account(user1):
    try:
        account = Account.objects.get(user=user1)
    except Account.DoesNotExist:
        account = None
    return account

def get_user_account(user1):
    try:
        account = Account.objects.get(user=user1)
    except Account.DoesNotExist:
        account = Account(
            home_dir=user1.username,
            user=user1
        )
        account.save()
        file_create_dir(USER_FILE_ROOT + account.home_dir)
    return account

def set_user_account(account1, obj):
    for key in obj.keys():
        #if key in dir(Account):
        account1[key] = obj[key]
    
    account1.save()

def get_rendered_string(request,filename,context):
    info = check_language(request)
    t = loader.get_template(filename)
    obj = {'language':info['language'],'files':[] }
    obj.update(context)
    c = Context(obj)
    return t.render(c)

def get_user_projects(request):
    try:
        projects = Project.objects.all().filter(user=request.user)
    except Project.DoesNotExist:
        projects = []
    return True,get_rendered_string(request,"template_paragraph_project.html",{'projects':projects})

def get_user_project_file(request,project):
    # get files from the project
    directory = USER_FILE_ROOT + request.user.username + "/" + project
    files = file_list_file(directory)
    return files

def set_user_project(user1, project_name):
    # if project already exist, return False
    try:
        projet = Project.objects.get(user=user1, name = project_name)
    except Project.DoesNotExist:
        project = Project(
            name = project_name,
            modified_datetime = datetime.datetime.now(),
            user = user1,
            publicity = "private",
            description = ""
        )
        project.save()
        file_create_dir(USER_FILE_ROOT + user1.username + "/" + project_name)
        return True, "project create OK"

    return False, "project name already exist:" + project_name
    
def set_user_file(user1,content):
    obj = json.loads(content)
    directory = USER_FILE_ROOT + user1.username + '/' + obj["project"] + '/'
    os.chdir(directory)

    name =  obj["name"]
    # check filename exist?
    if(file_check_exist(name)):
        return False,"File name exists"
    
    # create file ,and file.info under directory
    file_content = {}
    info_content = {}
    info_content["type"] = obj["type"]
    info_content["description"] = obj["description"]
    info_content["datetime_modified"] = ""
    info_content["datetime_created"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # write information into the file then leave
    try:
        file_create_file(name,json.dumps(file_content))
    except:
        return False, "create file NOK:" + obj["name"]
    try:
        file_create_file(name + ".info", json.dumps(info_content))
    except:
        return False,"file create NOK:" + obj["name"] + ".info"
    return True, "file create OK:" + obj["name"]

###########################################

def get_from_name(request,name,content):
    if name == "project":
        #return True, get_rendered_string(request,"template_paragraph_project.html", {})
        return get_user_projects(request)
    elif name == "account":
        #file_create_a_hello()
        # if the user don't have an account create one,
        # otherwise forward the account to the template render
        user_account = get_user_account(request.user)
        return True,get_rendered_string(request,"template_paragraph_account.html",{'account':user_account})
    elif name == "file":
        files = get_user_project_file(request, content)
        return True,get_rendered_string(request,"template_paragraph_file.html",{'project':content, 'files':files})
    else:
        return False,""

# content is a string, need to change to object
def set_from_name(request,name,content):
    if name == "create_project":
        return set_user_project(request.user,content)
    elif name == "create_file":
        return set_user_file(request.user,content)
    elif name == "account":
        user_account = get_user_account(request.user)
        obj = json.loads(content)
        set_user_account(user_account, obj)
        return True,"Save OK"
    else:
        return False, ""

# this is the entry point of ajax get function
@need_login
def get(request):
    message = {}
    if request.is_ajax() and request.method == "POST":
        name = request.POST["name"]
        if "content" not in request.POST.keys():
            content = {}
        else:
            content = request.POST["content"]
        status, return_str = get_from_name(request,name,content)
        message["content"]= return_str
        if status:
            message["success"]= "yes"
        else:
            message["success"]= "no"
    else:
        message = {"text":"Not Ajax","success":"no"}
    return HttpResponse(json.dumps(message),content_type="application/json")

@need_login
def set(request):
    message = {}
    if request.is_ajax() and request.method == "POST":
        name = request.POST["name"]
        content = request.POST["content"]
        status,return_str = set_from_name(request,name,content)
        message["content"]= return_str

        if status:
            message["success"]= "yes"
        else:
            message["success"]= "no"
    else:
        message = {"text":"Not Ajax","success":"no"}
    return HttpResponse(json.dumps(message),content_type="application/json")

