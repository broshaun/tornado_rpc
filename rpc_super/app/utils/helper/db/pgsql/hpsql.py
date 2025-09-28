import polars as pl
from datetime import datetime
from copy import deepcopy


class CRUD(object):
    '''
    PgSQL增删改查帮助类
    参数:
        session <- 会话缓存；
        con <- 数据库连接；
        uid <- 认证用户ID。
    '''
    def __init__(self, dbcon, schema, table):
        self.con = dbcon
        self.schema = schema
        self.table = table
        self.uid = 0
        self.current_time = lambda:datetime.now()
        self.timestamp = lambda:round(datetime.now().timestamp() * 1000000)
 
    def begin(self):
        '''开始事务'''
        self.con.begin()

    def commit(self):
        '''提交事务
        注意：self.lastid 和 self.rowcount 必须在提交事务后获取
        '''
        self.con.commit()
        self.lastid = self.con.lastid
        self.rowcount = self.con.rowcount
       
    def insert(self, **kwargs):
        '''插入数据
        参数：
            kwargs {column: value ...}
        返回：
            lastid 新建ID
        '''
        params = deepcopy(kwargs)
        params['creator'] = self.uid
        params['create_time'] = self.current_time()
        params['timestamp'] = self.timestamp()
        params['is_delete'] = False
        columnSql = ', '.join(f'"{key}"' for key in params)
        valueSql = ', '.join(f'%({key})s' for key in params)      
        sqltext = f''' INSERT INTO "{self.schema}"."{self.table}"({columnSql}) VALUES ({valueSql}) RETURNING id '''
        self.con.insert(sqltext, **params)
    
    def delete(self, id):
        '''删除数据
        参数：
            idList <- 要删除数据的Id列表
        返回：
            rowcount
        '''
        sqltext = f""" UPDATE "{self.schema}"."{self.table}" SET "is_delete" = TRUE, "timestamp" = '{self.timestamp()}' WHERE "id" = %(id)s """
        self.con.modify(sqltext, id = id)
    
    def update(self, id, **kwargs):
        '''修改指定ID数据
        参数：
            params = {}
            kwargs {column: value ...}
        返回：
            rowcount
        '''
        params = {}
        for i in kwargs:
            if kwargs[i] is not None:
                params[i] = kwargs[i]
        setSql = ', '.join(f' "{key}" = %({key})s ' for key in params)
        sqltext = f""" UPDATE "{self.schema}"."{self.table}" SET {setSql}, "timestamp" = '{self.timestamp()}' WHERE "id" = %(id)s """
        self.con.modify(sqltext, id = id, **params)
    
    def search(self, where=dict()) -> pl.DataFrame:
        '''
         参数：
            where {column:value ...}
        '''
        params = dict()
        where_sql = ''
        for k in where:
            params[k] = where[k]
            where_sql = where_sql + f' AND "{k}" = %({k})s'
        sql = f""" SELECT * FROM "{self.schema}"."{self.table}" WHERE "is_delete" IS FALSE {where_sql} """
        return self.con.polars_get_database(sql, params=params)

    def bysql(self,sqltext:str,where={}) -> pl.DataFrame:
        '''sql查询：
        参数：
            sqltext：
                执行sqltext语句，sqltext自带 %(params)s 占位符。
            params：
                字典数据key-values
        返回 dataframe
        '''
        params:dict = deepcopy(where)
        return self.con.polars_get_database(sql=sqltext,params=params)
    


        







   
            


        
    
        
        
        
