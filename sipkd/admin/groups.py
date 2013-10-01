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

from sqlalchemy.exc import DBAPIError
import json
from sipkd.views.views import sipkd_init
from sipkd.views.views import json_format
from sipkd.admin.models.apps import osApps
from sipkd.admin.models.groups import osGroups, osGroupModules


BLANK_ROW = dict(form_visible = 0,
                 id = '',
                 kode = '',
                 nama ='',
                 locked = 0)


class osfGroupValid(colander.MappingSchema):
    kode = colander.SchemaNode(colander.String())
    nama = colander.SchemaNode(colander.String())
    locked = colander.SchemaNode(
                    colander.Integer(),
                    missing = 0,) 
                    
class osfGroupsViews(object):
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
    @view_config(route_name = 'admin_groups',
                 renderer   = '../templates/admin/groups.pt')
    def home(self):
        session = self.request.session
        request = self.request
        datas=sipkd_init(self.request, self.context)
        resource = None
        if session['logged'] <> 1:
           return HTTPFound(location='/logout') 
        url = request.resource_url(resource)
        return dict(datas=datas, url=url)
#grid
    @view_config(route_name='admin_groups_grid', renderer='json')
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
                "iTotalRecords" : osGroups.get_count(),
                "sOrder":'kode',
                'aaData':[]}
                
        grids.update({"iTotalDisplayRecords" :osGroups.get_count_filtered(grids)})
        aColumns=('id','kode','nama','defsign','locked')
        sOrder = ""; 
        if 'iSortCol_0' in req.GET :
            for i in range(0, int(req.GET['iSortingCols']) ):
                if req.GET['bSortable_%s' % req.GET['iSortCol_%d' % i]] == "true":
                    sOrder = ''.join((sOrder, aColumns[ int(req.GET['iSortCol_%d' % i])] ,' ', req.GET['sSortDir_%s' % i] ,", "))
            
        grids.update({'sOrder' : sOrder[:-2]})  
        print   'sOrder' , sOrder[:-2]

        opts = osGroups.get_row_limits(grids)
        for opt in opts: 
            checked = opt.locked==1 and "checked" or ""
            grids['aaData'].append([opt.id, opt.kode, opt.nama, opt.locked
            ])
      
        return grids

       
# form
    @view_config(route_name='admin_groups_form',
                 renderer='../templates/admin/groups_form.pt')
    def form(self):
        request = self.request
        session = request.session
        resource = None
        url=request.resource_url(resource)
        datas=sipkd_init(self.request, self.context)

        if session['logged']<>1:
           return HTTPFound(location='/logout') 
        
        fields = self.request.matchdict
        datas.update(BLANK_ROW)
        datas['form_visible'] = 0
        
        if 'id' in fields:
            print 'id', fields['id']
            datas['id']=fields['id']
            if datas['id'].isdigit() and int(datas['id'])>0:
                data = osGroups.get_by_id(datas['id'])
                if data:
                    datas['form_visible'] = 1
                    datas['found'] = 1
                    datas.update(data.to_dict())
            else:
                datas['id']=0
                datas['headers']=[]
                
        schema = osfGroupValid()
        myform = Form(schema, buttons=('submit',))
        if 'btn_save' in self.request.POST:
            controls = self.request.POST.items()
            data2=dict((x, y) for x, y in controls)
            datas.update(data2)
            try:
                appstruct = myform.validate(controls)
                datas.update(appstruct)
                osGroups.edit(datas)
            except ValidationFailure, e:
                datas['message'] = 'Silahkan Lengkapi Isian Form'
                return dict(datas = datas, url = url)
        
            data2 = dict(BLANK_ROW)
            data2['id'] = 0
            datas.update(data2)
        return dict(datas = datas, url = url)

#cek kode
    @view_config(route_name='admin_groups_cek',
                 renderer='json')
    def admin_groups_cek(self):
        fields = self.request.matchdict
        datas={}
        datas['found'] = 0
        datas['kode'] = fields['kode']
        if datas['kode']:
            d = osGroups.get_by_kode(datas['kode'])
            if d:
                datas['found'] = 1
                datas.update(d.to_dict())
        return json.dumps(datas, default=json_format)

#gridmodule
    @view_config(route_name='admin_gmodule_grid', renderer='json')
    def gridmodule(self):
        fields = self.request.matchdict
        resource = None
        opts = osGroupModules.get_rows([fields['app_id'], fields['group_id']])
        
        grids={"aaData":[]}
        for opt in opts: 
            read_checked = opt.reads==1 and "checked" or ""
            write_checked = opt.writes==1 and "checked" or ""
            insert_checked = opt.inserts==1 and "checked" or ""
            delete_checked = opt.deletes==1 and "checked" or ""
            
            grids['aaData'].append([opt.module_id, opt.module_kode, opt.module_nama, 
                                    '<input type="checkbox" onchange="update_stat(%d,this.checked,1);" id="R%d" name="R" %s>' % (opt.module_id, opt.module_id, read_checked),
                                    '<input type="checkbox" onchange="update_stat(%d,this.checked,2);" id="W%d" name="W" %s>' % (opt.module_id, opt.module_id, write_checked),
                                    '<input type="checkbox" onchange="update_stat(%d,this.checked,3);" id="I%d" name="I" %s>' % (opt.module_id, opt.module_id, insert_checked),
                                    '<input type="checkbox" onchange="update_stat(%d,this.checked,4);  id="D%d" name="D" %s>' % (opt.module_id, opt.module_id, delete_checked),
                                    ])
        return grids
#gridmodule
    @view_config(route_name='admin_gmodule_update_stat', renderer='json')
    def update_stat(self):
        fields = self.request.matchdict
        fields['state'] = int(fields['state'])
        row = osGroupModules.edit(fields)
        #row.save(user) # Bagaimana mendapatkan user ? (sugiana)
        row.save()
        return dict(success = 1)
        
        
        
