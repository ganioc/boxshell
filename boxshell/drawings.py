# -*- coding: utf-8 -*-                        
from django.shortcuts import redirect, render_to_response 
from django.contrib.auth.models import User
from django.template import Context, Template
from django.template.loader import get_template
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
    
@need_login
def lib(request):
    info = check_language(request)
    title = "元件库" if info['language']=="zh-CN" else 'Symbol Library'

    myuser = request.user
    user_account = return_user_account(myuser)

    return return_page(request,'drawings/bs_lib.html',
                       title,
                       {'language':info['language'],
                        'user':myuser
                        })

@need_login
def newlib(request):
    info = check_language(request)
    title = "元件库" if info['language']=="zh-CN" else 'Symbol Library'

    myuser = request.user
    user_account = return_user_account(myuser)

    return return_page(request,'drawings/bs_newlib.html',
                       title,
                       {'language':info['language'],
                        'user':myuser
                        })

@need_login
def newboard(request):
    info = check_language(request)
    title = "画板" if info['language']=="zh-CN" else 'Board'

    myuser = request.user
    user_account = return_user_account(myuser)
    mycontext = {'user':myuser,
                 'language':info['language']
             }

    sch_template = get_template("drawings/board_sch_template.html");
    sch_context = Context(mycontext);
    sch_html = sch_template.render(sch_context)

    pcb_template = get_template("drawings/board_pcb_editor_template.html");
    pcb_context = Context(mycontext);
    pcb_html = pcb_template.render(pcb_context);

    symbol_template = get_template("drawings/board_symbol_lib_template.html");
    symbol_context = Context(mycontext);
    symbol_html = symbol_template.render(symbol_context);

    return return_page(request,'drawings/bs_board.html',
                       title,
                       {'language':info['language'],
                        'user':myuser,
                        'section3':symbol_html,
                        'section4':sch_html,
                        'section5':pcb_html
                        })

