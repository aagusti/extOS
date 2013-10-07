from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.renderers import JSON

from models import (
    DBSession,
    Base,
    )
    
#from security import get_user


def add_route(config, rc):
    for c, v in rc:
        config.add_route(c, v)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(settings=settings, session_factory=my_session_factory)
#    config.add_request_method(get_user, 'user', reify=True)

    config.add_renderer('json', JSON(indent=0))    
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('home', '/')
    config.add_route('main', '/main')
    config.add_route('home1', '/home1')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('admin', '/admin')
    config.add_route('admin_apps', '/admin/apps')
    config.add_route('admin_apps_grid', '/admin/apps/grid')
    config.add_route('admin_apps_update_stat', '/admin/apps/update_stat/{id}/{value}')
    config.add_route('hello', '/hello')
    config.add_route('get_pesan', '/get_pesan')
    
    from admin_route import admin_route
    add_route(config, admin_route)
    
    from pbb_route import pbb_route
    add_route(config, pbb_route)
    
    from pbbm_route import pbbm_route
    add_route(config, pbbm_route)
    

    from apbd_route import apbd_route
    add_route(config, apbd_route)
    
    from aset_route import aset_route
    print aset_route
    add_route(config, aset_route)

    config.scan()
    return config.make_wsgi_app()
