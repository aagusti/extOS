from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, or_, func
from sipkd.models import Base, DBSession, osSipkdModel


class osUsers(Base, osSipkdModel):
    __tablename__ = 'users'
    kode = Column(String(32), unique=True, nullable=False)
    nama = Column(String(64))
    passwd = Column(String(64))
    nip = Column(String(32))
    locked = Column(Integer, default=0, nullable=False)
        
    @classmethod
    def get_by_nama(cls, nama):
        return DBSession.query(cls).filter(cls.nama==nama).first()
    
    @classmethod
    def get_by_kode(cls, kode):
        q = DBSession.query(cls).filter(cls.kode==kode)
        return q.first()

    @classmethod
    def get_count_filtered(cls,data):
        return DBSession.query(func.count(cls.id)).filter(or_(
            cls.kode.ilike(''.join(("%",data['sSearch'],'%'))),
            cls.nama.ilike(''.join(("%",data['sSearch'],'%'))),
            )).first()
        
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
 

class osUserGroups(Base, osSipkdModel):
    __tablename__ = 'user_groups'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    groups = relationship('osGroups', foreign_keys=[group_id])
    users = relationship('osUsers', foreign_keys=[user_id])
        
    @classmethod
    def get_by_users(cls, id):
        return DBSession.query(cls).filter(cls.user_id == id).all()

    @classmethod
    def tambah(cls, datas):
        data=cls(datas)
        DBSession.add(data)
        return(true)
        
    @classmethod
    def edit(cls, data):
        q = DBSession.query(cls).filter(cls.group_id == data['group_id'],
                                        cls.user_id == data['user_id'])
        row = q.first()
        if not row:
            row = cls()
            row.from_dict(data)
            return row
        
    @classmethod
    def get_by_app_id(cls, id):
        if id.isdigit() and int(id)>0:
            return DBSession.query(cls).filter(
                       cls.app_id == id
                       ).all()
        else:
            return cls.get_rows()

