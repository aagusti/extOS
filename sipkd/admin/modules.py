from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
import colander
from deform import Form
from deform import ValidationFailure


#from sqlalchemy import *
#from sipkd.models import *
from sqlalchemy.exc import DBAPIError
import json
from sipkd.views.views import sipkd_init
from sipkd.views.views import json_format
from sipkd.admin.models.apps import osApps
from sipkd.admin.models.modules import osModules

class osfModuleValid(colander.MappingSchema):
    kode = colander.SchemaNode(colander.String())
    nama = colander.SchemaNode(colander.String())
    app_id = colander.SchemaNode(colander.Integer())
    locked = colander.SchemaNode(
                    colander.Integer(),
                    missing = 0,) 
                    
class ModulesViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        renderer = get_renderer("../templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        
        renderer = get_renderer("../templates/main.pt")
        self.main = renderer.implementation().macros['main']

        renderer = get_renderer("../templates/admin/nav.pt")
        self.nav = renderer.implementation().macros['nav']
#home        
    @view_config(route_name = 'admin_modules',
                 renderer   = '../templates/admin/modules.pt')
    def home(self):
        session = self.request.session
        request = self.request
        datas=sipkd_init(self.request, self.context)
        resource = None
        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        url=request.resource_url(resource)
        if self.request.session['sa']==1:
            modules = osModules.get_rows()
            
        else:
            pass
  
        return dict(datas=datas, url=url)
#grid
    @view_config(route_name='admin_modules_grid', renderer='json')
    def grid(self):
        fields = self.request.matchdict
        resource = None
        opts = osModules.get_by_app_id(fields['id'])
        
        grids={"aaData":[]}
        for opt in opts: 
            checked = opt.locked==1 and "checked" or ""
            grids['aaData'].append([opt.id, opt.apps.nama, opt.kode, opt.nama, opt.locked
            ])
        return grids
        
        
# form
    @view_config(route_name='admin_modules_form',
                 renderer='../templates/admin/modules_form.pt')
    def form(self):
        request = self.request
        session = request.session
        resource = None
        url=request.resource_url(resource)
        datas=sipkd_init(self.request, self.context)
        datas.update(osModules.BlankRow())

        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        
        fields = self.request.matchdict
        datas.update(osModules.BlankRow())
        datas['form_visible'] = 0
        
        if 'id' in fields:
            datas['id']=fields['id']
            if datas['id'].isdigit() and int(datas['id'])>0:
                data = osModules.row2dict(osModules.get_by_id(datas))
                if data:
                    datas['form_visible'] = 1
                    datas['found'] = 1
                    datas.update(data)
            else:
                datas['id']=0
                datas['headers']=[]
                
        schema = osfModuleValid()
        myform = Form(schema, buttons=('submit',))
        if 'btn_save' in self.request.POST:
            controls = self.request.POST.items()
            data2=dict((x, y) for x, y in controls)
            datas.update(data2)
            #datas['message']='Berhasil'
            try:
                appstruct = myform.validate(controls)
                datas.update(appstruct)
                osModules.edit(datas)
            except ValidationFailure, e:
                datas['message'] = 'Silahkan Lengkapi Isian Form'
                return dict(datas = datas, url = url)
        
            data2=osModules.BlankRow()
            datas.update(data2)
            #return dict(datas=datas)
        return dict(datas = datas, url = url)

#cek kode
    @view_config(route_name='admin_modules_cek',
                 renderer='json')
    def admin_modules_cek(self):
        fields = self.request.matchdict
        datas={}
        datas['found'] = 0
        datas['kode'] = fields['kode']
        if datas['kode']:
            d=osModules.row2dict(osModules.get_by_kode(datas))
            if d: 
                datas['found'] = 1
                datas.update(d)
        return json.dumps(datas, default=json_format)
