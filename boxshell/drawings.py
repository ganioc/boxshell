# -*- coding: utf-8 -*-                        
from django.shortcuts import redirect, render_to_response 
from django.contrib.auth.models import User
from command.views import need_login, check_language, return_user_account, return_page

@need_login
def sch(request, project, filename):
    info = check_language(request)
    title = "原理图" if info['language']=="zh-CN" else 'Schematic'

    myuser = request.user
    user_account = return_user_account(myuser)

    return return_page(request,'drawings/bs_sch.html',
                       title,
                       {'language':info['language'],
                        'user':myuser,
                        'project':project,
                        'file':filename
                        })
    
