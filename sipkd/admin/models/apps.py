import sys
from sipkd.models import DBSession, Base, osSipkdModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship



class osApps(osSipkdModel, Base):
    __tablename__ = 'apps'
    kode = Column(String(64), nullable=False, unique=True)
    nama = Column(String(64), nullable=False, unique=True)
    locked = Column(Integer, nullable=False, default=0)
    modules = relationship('osModules', backref='osApps')
        
    @classmethod
    def get_rows(cls):
        return DBSession.query(cls).order_by('kode').all()
        
    @classmethod
    def get_active_rows(cls):
        return DBSession.query(cls).filter(cls.locked==0).order_by('kode').all()

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()
        
    @classmethod
    def get_by_nama(cls, nama):
        return DBSession.query(cls).filter(cls.nama==nama).first()
    
    @classmethod
    def get_by_kode(cls,kode):
            return DBSession.query(cls).filter(cls.kode==kode).first()        

    @classmethod
    def edit(cls, data):
        DBSession.merge(cls(data))
        
    @classmethod
    def edit_locked(cls, data):
        a = DBSession.query(cls).filter_by(id=data['id']).first()
        a.locked = data['value']
        try: 
            DBSession.merge(a)
            return True
        except:
            print sys.exc_info()

