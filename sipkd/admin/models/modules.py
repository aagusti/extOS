from sipkd.models import * 
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
import types
class osModules(Base):
    __tablename__ = 'modules'
    #__autoload__  = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    kode = Column(String(20))
    nama = Column(String(50))
    locked = Column(Integer)
    app_id = Column(Integer, ForeignKey("apps.id"))
    apps = relationship("osApps")

    def __init__(self,data):
        #print data['id']
        if data['id'].isdigit() and int(data['id'])>0:
            self.id = data['id']
        self.kode = data['kode']
        self.nama = data['nama']
        self.locked = data['locked']
        self.app_id = data['app_id']
        
    @classmethod
    def BlankRow(cls):
            return {'form_visible':0,
                    'id' : '',
                    'kode' : '',
                    'nama' : '',
                    'locked' : 0,
                    'app_id' : '',

                  }
                  
    @classmethod
    def row2dict(cls,row):
        d = {}
        if row:
            for column in row.__table__.columns:
                d[column.name] = getattr(row, column.name)
        return d
        
    @classmethod
    def tambah(cls, datas):
        data=cls(cls(datas))
        DBSession.add()
            
    @classmethod
    def edit(cls, data):
        DBSession.merge(cls(data))
            
    @classmethod
    def hapus(cls, data):
        DBSession.query(cls).filter(           
              cls.id==data['id']
            ).delete()

    @classmethod
    def get_count(cls):
        return DBSession.query(func.count(cls.id)).first()

    @classmethod
    def get_count_filtered(cls,data):
        return DBSession.query(func.count(cls.id)).filter(or_(
            cls.kode.ilike(''.join(("%",data['sSearch'],'%'))),
            cls.nama.ilike(''.join(("%",data['sSearch'],'%'))),
            )).first()
        
    @classmethod
    def get_by_kode(cls, data):
        return DBSession.query(cls).filter(
                  cls.kode==data['kode']
                ).first()
        
    @classmethod
    def get_by_id(cls, data):
        return DBSession.query(cls).filter(
                  cls.id==data['id']
                ).first()

    @classmethod
    def get_by_nama(cls, data):
        return DBSession.query(cls).filter(
                       cls.nama.like( '%s%' % data['nama'])
                       ).first()
    
    @classmethod
    def get_rows(cls):
        return DBSession.query(cls).order_by('kode').all()
        
    
    @classmethod
    def get_row_limits(cls,data):
        if data['sSearch']:
            return DBSession.query(cls).filter(or_(
                      cls.kode.ilike(''.join((data['sSearch'],'%'))),
                      cls.nama.ilike(''.join((data['sSearch'],'%'))),
                        )).order_by(data['sOrder']) \
                .limit(data['iDisplayLength']) \
                .offset(data['iDisplayStart']) \
                .all()
        else:
            return DBSession.query(cls).order_by(data['sOrder']) \
                .limit(data['iDisplayLength']) \
                .offset(data['iDisplayStart']) \
                .all()
        
    @classmethod
    def get_by_app_id(cls, id):
        if id.isdigit() and int(id)>0:
            return DBSession.query(cls).filter(
                       cls.app_id == id
                       ).all()
        else:
            return cls.get_rows()


                       