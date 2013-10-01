import sys
from sipkd.models import Base, osSipkdModel
from modules import osModules
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, ForeignKey, or_
from sqlalchemy.sql import literal_column


class osGroups(Base, osSipkdModel):
    __tablename__ = 'groups'
    kode = Column(String(20), unique=True)
    nama = Column(String(50), unique=True)
    locked = Column(Integer,  default=0)
    modules = relationship('osGroupModules', backref='osGroups')

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
    def get_by_nama(cls, data):
        return DBSession.query(cls).filter(
                       cls.nama.like( '%s%' % data['nama'])
                       ).first()
    
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


class osGroupModules(Base, osSipkdModel):
    __tablename__ = 'group_modules'
    group_id = Column(Integer, ForeignKey('groups.id'))
    module_id = Column(Integer, ForeignKey('modules.id'))
    reads = Column(Integer, default=0)
    writes = Column(Integer, default=0)
    inserts = Column(Integer, default=0)
    deletes = Column(Integer, default=0)
    groups = relationship('osGroups')
    modules = relationship('osModules')

    def set_state(self, state, value):
        state_fields = [ '', 'reads', 'writes', 'inserts', 'deletes']
        field = state_fields[state]
        setattr(self, field, value)

    @classmethod
    def get_rows(cls, app_id, group_id):
        q1 =  DBSession.query(osModules.id.label('module_id'),
                  osModules.kode.label('module_kode'),
                  osModules.nama.label('module_nama'),
                  literal_column('0').label('reads'),
                  literal_column('0').label('writes'),
                  literal_column('0').label('inserts'),
                  literal_column('0').label('deletes'),
              ).filter(osModules.app_id == app_id) \
               .filter(osModules.id.notin_(
                  DBSession.query(cls.module_id).filter(cls.group_id==group_id)))
        q2 =  DBSession.query(osGroupModules.module_id.label('module_id'),
                  osModules.kode.label('module_kode'),
                  osModules.nama.label('module_nama'),
                  osGroupModules.reads.label('reads'),
                  osGroupModules.writes.label('writes'),
                  osGroupModules.inserts.label('inserts'),
                  osGroupModules.deletes.label('deletes'),
              ).join(osModules) \
              .filter(osGroupModules.group_id == group_id) \
              .filter(osModules.app_id == app_id)   
        return q1.union(q2).all()

    @classmethod
    def edit(cls, data):
        q = DBSession.query(cls).filter(cls.group_id == data['gid'],
                                        cls.module_id == data['mid'])
        row = q.first()
        if not row:
            row = cls(group_id=data['gid'], module_id=data['mid'])
        row.set_state(data['state'], data['val'])
        return row
        
    @classmethod
    def get_by_app_id(cls, id):
        if id.isdigit() and int(id) > 0:
            return DBSession.query(cls).filter(cls.app_id == id).all()
        return cls.get_rows()

