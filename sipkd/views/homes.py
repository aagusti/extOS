from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy.exc import DBAPIError
from sipkd.models import *
from sipkd.views.views import *

def get_logged(request):
    session = request.session
    if 'logged' in session:
        r = '<div class="btn-group pull-right">'
        r += '  <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"></a>'
        r += '  <ul class="dropdown-menu pull-right">'
        r += '  <li><a href="#">Ubah Password</a></li>'
        r += '  <li><a href="/logout">Logout</a></li>'
        r += '  </ul>'
        r += '</div>'
            
    return r or ''
    
def get_apps(request):
    return ''

    
class SipkdViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        renderer = get_renderer("../templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']

        
    @view_config(route_name='home',
                 renderer='../templates/home.pt')
    def home(self):
        datas=sipkd_init(self.request, self.context)
        return dict(message = 'Silahkan Login',
                    datas=datas)
                    
    
    @view_config(route_name='login',
                 renderer='json')
    def login(self):
        from sipkd.admin.models.users import osUsers
        
        request = self.request
        login_url = request.resource_url(request.context, '/login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/' # never use the login form itself as came_from
        message = ''
        login = ''
        passwd = ''
        datas=sipkd_init(self.request, self.context)
        if 'userid' in request.params:
            login = request.params['userid']
            xpasswd = request.params['passwd']
            row = osUsers.get_by_kode(login)
            if row and row.passwd==xpasswd :
                
                headers = remember(request, login)
                session = request.session
                session['userid'] = row.kode
                session['usernm'] = row.nama
                session['user_id']=row.id
                session['logged']=1
                if login=='sa':
                    session['sa'] = 1
                    return {'success': True, 'redirect': '/admin'}
                    return HTTPFound(location='/admin',
                                 headers=headers)
                else: session['sa']=0
                
                return HTTPFound(location='/main',
                                 headers=headers)
            datas['message'] = 'Login Gagal'
            datas['title']="Login"
        return  {'success': False, 'errormsg':'Login Gagal'}
            
    @view_config(route_name="logout", renderer="../templates/home.pt")
    def logout(self):
        headers = forget(self.request)
        session = self.request.session
        session['logged']=0
        url = self.request.resource_url(self.context, '/')
        return HTTPFound(location=url, headers=headers)

    @view_config(route_name="main", renderer="../templates/main.pt")
    def main(self):
        session = self.request.session

        datas = sipkd_init(self.request, self.context)
        if session['logged']==0:
            return HTTPFound(location='/')
        return dict(datas=datas or null)
