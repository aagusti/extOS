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
from sipkd.admin.models.users import osUsers, osUserGroups
from sipkd.admin.models.groups import osGroups


BLANK_ROW = dict(
    form_visible = 0,
    id = '',
    kode = '',
    nama = '',
    passwd = '',
    nip = '',
    locked = 0)
    

class osfGroupValid(colander.MappingSchema):
    kode = colander.SchemaNode(colander.String())
    nama = colander.SchemaNode(colander.String())
    locked = colander.SchemaNode(
                    colander.Integer(),
                    missing = 0,) 
                    
class osfusersViews(object):
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
    @view_config(route_name = 'admin_users',
                 renderer   = '../templates/admin/users.pt')
    def home(self):
        session = self.request.session
        request = self.request
        datas=sipkd_init(self.request, self.context)
        resource = None
        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        url=request.resource_url(resource)
        #if self.request.session['sa']==1:
        #    users = osusers.get_rows()
            
        #else:
        #    pass
        return dict(datas=datas, url=url)
#grid
    @view_config(route_name='admin_users_grid', renderer='json')
    def grid(self):
        resource = None
        req = self.request
        grids={ 'iDisplayLength':  'iDisplayLength' in req.GET and  req.GET['iDisplayLength'].isnumeric() and req.GET['iDisplayLength'] or 15,
                'iDisplayStart': 'iDisplayStart' in req.GET and  req.GET['iDisplayStart'].isnumeric() and req.GET['iDisplayStart'] or 0,
                'iSortCol_0': 'iSortCol_0' in req.GET and  req.GET['iSortCol_0'].isnumeric() and req.GET['iSortCol_0'] or 0,
                'iSortingCols': 'iSortingCols' in req.GET and  req.GET['iSortingCols'].isnumeric() and req.GET['iSortingCols'] or 1,
                'sEcho': 'sEcho' in req.GET and  req.GET['sEcho'].isnumeric() and req.GET['sEcho'] or 1,
                'sSearch': 'sSearch' in req.GET  and req.GET['sSearch'] or "",
                'sSortDir_0': 'sSortDir_0' in req.GET and req.GET['sSortDir_0'] or "asc",
                "iTotalRecords" : osUsers.get_count(),
                "sOrder":'kode',
                'aaData':[]}
                
        grids.update({"iTotalDisplayRecords" :osUsers.get_count_filtered(grids)})
        aColumns=('id','kode','nama','defsign','locked')
        sOrder = ""; 
        if 'iSortCol_0' in req.GET :
            for i in range(0, int(req.GET['iSortingCols']) ):
                if req.GET['bSortable_%s' % req.GET['iSortCol_%d' % i]] == "true":
                    sOrder = ''.join((sOrder, aColumns[ int(req.GET['iSortCol_%d' % i])] ,' ', req.GET['sSortDir_%s' % i] ,", "))
            
        grids.update({'sOrder' : sOrder[:-2]})  
        print   'sOrder' , sOrder[:-2]

        opts = osUsers.get_row_limits(grids)
        for opt in opts: 
            checked = opt.locked==1 and "checked" or ""
            grids['aaData'].append([opt.id, opt.kode, opt.nama, opt.locked
            ])
      
        return grids

       
# form
    @view_config(route_name='admin_users_form',
                 renderer='../templates/admin/users_form.pt')
    def form(self):
        request = self.request
        session = request.session
        resource = None
        url=request.resource_url(resource)
        datas=sipkd_init(self.request, self.context)
        datas.update(BLANK_ROW)

        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        
        fields = self.request.matchdict
        datas.update(BLANK_ROW)
        datas['form_visible'] = 0
        
        if 'id' in fields:
            datas['id'] = fields['id']
            if datas['id'].isdigit() and int(datas['id'])>0:
                data = osUsers.get_by_id(datas)
                if data:
                    datas['form_visible'] = 1
                    datas['found'] = 1
                    datas.update(data.to_dict())
            else:
                datas['headers'] = []
                
        schema = osfGroupValid()
        myform = Form(schema, buttons=('submit',))
        if 'btn_save' in self.request.POST:
            controls = self.request.POST.items()
            data2=dict((x, y) for x, y in controls)
            datas.update(data2)
            try:
                appstruct = myform.validate(controls)
            except ValidationFailure, e:
                datas['message'] = 'Silahkan lengkapi isian form'
                return dict(datas = datas, url = url)
            datas.update(appstruct)
            row = osUsers.edit(datas)
            row.save(request.user)
            datas.update(BLANK_ROW)
        return dict(datas = datas, url = url)

#cek kode
    @view_config(route_name='admin_users_cek',
                 renderer='json')
    def admin_users_cek(self):
        fields = self.request.matchdict
        datas={}
        datas['found'] = 0
        datas['kode'] = fields['kode']
        if datas['kode']:
            d = osUsers.get_by_kode(datas['kode'])
            if d:
                datas['found'] = 1
                datas.update(d.to_dict())
        return json.dumps(datas, default=json_format)

#gridgroups
    @view_config(route_name='admin_ugroups_grid', renderer='json')
    def grid_user_groups(self):
        fields = self.request.matchdict
        resource = None
        if 'user_id' in fields and fields['user_id'].isdigit():
          opts = osUserGroups.get_by_users(fields['user_id'])
          
          grids={"aaData":[]}
          for opt in opts: 
              
              grids['aaData'].append([opt.id, opt.groups.kode, opt.groups.nama, 
                             '<input type="button" onclick="remove(%d);" id="R%d" name="R%d" value="Remove">' % (opt.id, opt.id, opt.id),
                              ])
          return grids

#add group
    @view_config(route_name='admin_ugroups_add', renderer='json')
    def add_group(self):
        fields = self.request.matchdict
        row = osUserGroups.edit(fields)
        if row:
            #row.save(user) # Bagaimana mendapatkan user ? (sugiana)
            return dict(success = 1)
        return dict(success = 0)
        
        
#remove group
    @view_config(route_name='admin_ugroups_remove', renderer='json')
    def update_stat(self):
        fields = self.request.matchdict
        if 'id' in fields:
            if osUserGroups.delete(fields['id']):
                return {'success': 1}
        return {'success': 0}
            
#grid group avalilable
    @view_config(route_name='admin_ugroups_apps_grid', renderer='json')
    def grid_ugroup_apps(self):
        fields = self.request.matchdict
        print fields
        resource = None
        if 'app_id' in fields:
            opts = osGroups.get_rows()
            grids={"aaData":[]}
            for opt in opts: 
                grids['aaData'].append([opt.id, opt.kode, opt.nama, 
                           '<input type="button" onclick="add(%d);" id="R%d" name="R" value="Add">' % (opt.id, opt.id),
                            ])
            return grids
            
        
