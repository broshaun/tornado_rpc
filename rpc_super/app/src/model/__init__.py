
import functools
import inspect
from utils.suger.middle import JWT
from copy import deepcopy
import polars as pl
from utils.helper.db.pgsql import DBOpen


class PgSQL():

    def set_config(self, Postgres:DBOpen):
        self.pgsql = Postgres
        return self

    def open(self,schema, table):
        self.hpsql = self.pgsql.open(schema, table)
        usr = JWT.get_user()
        sub = usr.get('sub',"...")
        uid = usr.get('uid',0)
        self.hpsql.uid = uid
        self.alias = f"{sub}:{uid}"
        return self.hpsql

    def begin(self):
        self.hpsql.begin()

    def commit(self):
        self.hpsql.commit()

    def insert(self, **kwargs):
        return self.hpsql.insert(**kwargs)

    def delete(self, id, *ids):
        for i in (id, *ids):
            self.hpsql.delete(id=i)
        
    def update(self, id, *ids, **where):
        if isinstance(id, (list,tuple)):
            ids = (*id, *ids)
        else:
            ids = (id, *ids)
        for i in ids:
            self.hpsql.update(id=i, **where)
    
    def byid(self,id)->dict:
        '''查询id数据，返回dict'''
        for ss in self.hpsql.search(where={"id":id}).iter_rows(named=True):
            return ss
        
    def search(self, where=dict())->pl.DataFrame:
        return self.hpsql.search(where)
    

    def bysql(self,sqltext:str,where={}) -> pl.DataFrame:
        return self.hpsql.bysql(sqltext,where=where)

    def bysql_for_total_detail(self,sqltext:str,where={}):
        '''查询数据表
        参数：
            sqltext：
                执行sqltext语句，sqltext自带 %(params)s 占位符。
            params：
                字典数据key-values
        '''
        params:dict = deepcopy(where)
        size = int(params.pop('size',10))
        offset = size * (int(params.pop('offset',1))-1)
        
        sqltext = sqltext.replace('SELECT','SELECT COUNT(1)OVER()AS _total,',1)
        sqltext += ' LIMIT {:d} OFFSET {:d}'.format(size,offset)

        data = {}
        df = self.hpsql.bysql(sqltext,where=params)
        if not df.is_empty():
            data['total'] = df['_total'][0]
            data['detail'] = df.drop('_total')
            return data
        else:
            data['total'] = 0
            data['detail'] = pl.DataFrame()
    

    def __getattr__(self, name):
        if hasattr(self.hpsql, name):
            attr = getattr(self.hpsql, name) 
            if not callable(attr): # 如果不是方法，直接返回属性值
                return attr
            @functools.wraps(attr) # 保留签名和基础转发
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            wrapper.__signature__ = inspect.signature(attr) # 保留原始方法的签名提示
            return wrapper

            
         
         

 




