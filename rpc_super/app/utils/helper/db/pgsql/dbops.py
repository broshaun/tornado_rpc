# 数据库操作类
import polars as pl
from psycopg2 import pool


class PgDB():
    '''PostgreSQL连接'''
    PGPOOL:pool.SimpleConnectionPool=None
    def __init__(self,host,port,user,password,database):
        '''简单pgsql链接池管理'''
        self.state = "await"
        if not self.__class__.PGPOOL:
            self.__class__.PGPOOL = pool.SimpleConnectionPool(minconn=1, maxconn=150, user=user, password=password, host=host, port=port, database=database)
 
    
    @property
    def ping(self)->str:
        """预计返回`pong`"""
        while not self.__class__.PGPOOL.closed:
            try:
                conn = self.__class__.PGPOOL.getconn()
                with conn.cursor() as cur:
                    cur.execute("SELECT 'pong'")
                    for i in cur.fetchone():
                        return i
            except pool.PoolError:
                self.__class__.PGPOOL.closeall()
            finally:
                self.__class__.PGPOOL.putconn(conn)


    def begin(self):
        self.state = "ready"
        self.fnsqlist = []
        self.lastid = []
        self.rowcount = 0
        if self.ping != "pong": 
            raise Exception("pgsql ping is fail !")


    def commit(self):
        if self.state != "ready":
            raise Exception("PgDB DML commit(), begin() must be executed first.")
        try:
            conn = self.__class__.PGPOOL.getconn()
            for fnsql in self.fnsqlist:
                fnsql(conn)
            else:
                conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            self.state = "submit"
            self.__class__.PGPOOL.putconn(conn)

            
    def insert(self,sql,*args,**kwargs):
        '''
        执行SQL语句,返回插入ID
        参数类型：
            列表：(param1, param2, param3, param4 ...)
            字典：(param1=value1, param2=value2, param3=value3, param4=value4 ...)
            无参数
        返回 (+RETURNING id)：lastrowid
        '''
        if self.state != "ready":
            raise Exception("PgDB insert(), begin() must be executed first.")
        def fn(conn):
            with conn.cursor() as cur:
                if args:
                    cur.execute(sql,args)
                elif kwargs:
                    cur.execute(sql,kwargs)
                else:
                    cur.execute(sql)    
                self.lastid.append(*cur.fetchone())
        self.fnsqlist.append(fn)



    def modify(self,sql,*args,**kwargs):
        '''
        执行SQL语句,错误则回滚
        参数类型：
            列表：params is list
            字典：params is dict
            无参数 params is None
        返回：影响行数
        '''
        if self.state != "ready":
            raise Exception("PgDB modify(), begin() must be executed first.")
        def fn(conn):
            with conn.cursor() as cur:
                if args:
                    cur.execute(sql,args)
                elif kwargs:
                    cur.execute(sql,kwargs)
                else:
                    cur.execute(sql)
                self.rowcount += cur.rowcount
        self.fnsqlist.append(fn)


    def polars_get_database(self,sql,params={},*args,**kwargs) -> pl.DataFrame:
        if self.ping != "pong": raise Exception("pgsql ping is fail !")
        '''
        pandas查询方式，返回DataFrame格式数据
        '''
        try:
            conn = self.__class__.PGPOOL.getconn()
            execute_options = {"parameters": params}
            return pl.read_database(query=sql, connection=conn, execute_options=execute_options, *args, **kwargs) 
        except: raise
        finally: self.__class__.PGPOOL.putconn(conn)



        
        
        

