import json
import locale
try:
    locale.setlocale(locale.LC_ALL,  'id_ID.utf8')
    locale_ok = True
except locale.Error:
    locale_ok = False
    

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    String,
    Index,
    ForeignKey,
    func,
    Table,
    Float,
    BigInteger,
    Numeric,
    Date
    )
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension
from datetime import datetime

KD_PROPINSI  = '32'
KD_DATI2  = '79'

def money(n):
    return locale_ok and locale.format('%d', n, True) or '{0:,}'.format(n)
    

BUKUS = (("11","Buku 1"),
         ("12","Buku 1 - 2"),
         ("13","Buku 1 - 3"),
         ("14","Buku 1 - 4"),
         ("15","Buku 1 - 5"),
         ("22","Buku 2"),
         ("23","Buku 2 - 3"),
         ("24","Buku 2 - 4"),
         ("25","Buku 2 - 5"),
         ("33","Buku 3"),
         ("34","Buku 3 - 4"),
         ("35","Buku 3 - 5"),
         ("44","Buku 4"),
         ("45","Buku 4 - 5"),
         ("55","Buku 5"),)
         
BUKUR = [[0, 100000],
          [0, 100000], 
          [100000,1000000], 
          [1000000,2500000], 
          [2500000,5000000],
          [5000000,1000000000]
          ]

def to_json(inst, cls):
    
    """
    Jsonify the sql alchemy query result.
    """
    #convert = dict()
    #print x
    # add your coversions for things like datetime's 
    # and what-not that aren't serializable.
    #d = dict()
    """for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    #print d"""
    return {'a':'a'}  #json.dumps(d)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class BaseModel(object):
    id = Column(Integer, primary_key=True)
    
    def to_dict(self):
        values = {}
        for column in self.__table__.columns:
            values[column.name] = getattr(self, column.name)
        return values
        
    def from_dict(self, values):
        for column in self.__table__.columns:
            if column.name in values:
                setattr(self, column.name, values[column.name])

    @classmethod
    def get_rows(cls, order_by=[]):
        q = DBSession.query(cls)
        for field in order_by:
            q = q.order_by(field)
        return q.all()
        
    @classmethod
    def get_count(cls):
        return DBSession.query(func.count(cls.id)).first()
        
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()
        
    @classmethod
    def edit(cls, data):
        d = dict(data)
        if not d['id'].isdigit() or d['id'] == '0':
            del d['id']
        row = cls()
        row.from_dict(d)
        return row
        
    @classmethod
    def delete(cls, id):
        return DBSession.query(cls).filter(cls.id==id).delete()


class osSipkdModel(BaseModel):
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def create_uid(cls):
        return Column(Integer, ForeignKey('users.id'))
    
    @declared_attr
    def update_uid(cls):
        return Column(Integer, ForeignKey('users.id'))

    def save(self, user=None):
        self.updated = datetime.now()
        if user:
            self.update_uid = user.id
            if not self.create_uid:
                self.create_uid = user.id
        DBSession.add(self)


