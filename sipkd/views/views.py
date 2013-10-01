from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError

from sqlalchemy import Date
from decimal import Decimal
from sipkd.models import (
    DBSession,
    #osApp,
    )

from sipkd.admin.models.apps import osApps

def json_format(o):
    if type(o) is Date:
        return o.strftime("%d-%m-%Y")
    if type(o) is Decimal:
        return int(o)

        
        
def sipkd_init(request,context):
    datas={}
    datas['title']="OpenSIPKD"
    datas['message']="Silahkan Isi Form di bawah ini"
    datas['module']='module' in request.session and request.session['module'] or ""
    if 'logged' in request.session and request.session['logged']==1:
        datas['usernm']=request.session['usernm'], 
        if request.session['sa']==1:
            datas['opts']=osApps.get_active_rows()
            opts = osApps.get_active_rows()
    else:
        datas['usernm']=''
        datas['url']=request.resource_url(context, '/')
        request.session['logged']=0
    return datas

