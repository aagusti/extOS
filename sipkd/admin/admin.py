from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
#from sqlalchemy import *
#from sipkd.models import *
from sqlalchemy.exc import DBAPIError
import json
from sipkd.views.views import sipkd_init
from sipkd.views.views import json_format
from sipkd.admin.models.apps import osApps
                
class AdminViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        renderer = get_renderer("../templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        
        renderer = get_renderer("../templates/main.pt")
        self.main = renderer.implementation().macros['main']

        renderer = get_renderer("templates/nav.pt")
        self.nav = renderer.implementation().macros['nav']
        
    @view_config(route_name='admin',
                 renderer='templates/home.pt')
    def admin(self):
        session = self.request.session
        request = self.request
        session['module']='admin'
        resource = None
        datas=sipkd_init(self.request, self.context)
        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        opts=[dict(nama='ADMIN', kode='admin')]
        url=request.resource_url(resource)
        #url='a'
        if self.request.session['sa']==1:
            opts = osApps.get_rows()
            print opts
        else:
            pass
        return dict(datas=datas, url=url)
                    
    @view_config(route_name = 'admin_apps',
                 renderer   = '../templates/admin/apps.pt')
    def apps(self):
        session = self.request.session
        request = self.request
        datas=sipkd_init(self.request, self.context)
        resource = None
        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        url=request.resource_url(resource)
        if self.request.session['sa']==1:
            opts = osApps.get_rows()
            opts=[dict(nama='ADMIN', kode='admin')]
            print opts
        else:
            pass
  
        return dict(datas=datas, url=url)

    @view_config(route_name='admin_apps_grid', renderer='json')
    def appsgrid(self):
        resource = None
        opts = osApps.get_rows()
        
        grids={"aaData":[]}
        for opt in opts: 
            checked = opt.locked==1 and "checked" or ""
            grids['aaData'].append([opt.id, opt.nama, opt.kode,
            '<input type="checkbox" onchange="update_stat(%d,this.checked);" name="disabled" %s>' % (opt.id,checked)
            
            ])
        return grids
        #json.dumps(grids, 
        #                  default = json_format)
        

    @view_config(route_name='admin_apps_update_stat', renderer='json')
    def appupdate_stat(self):
        request = self.request
        fields = request.matchdict
        
        if osApps.edit_locked(fields)==True:
            return {'success':1}
        else:
            return {'success':0}

