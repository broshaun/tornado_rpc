import redis
import polars as pl
from io import BytesIO


class RedisDB():
    '''Redis缓存帮助类'''

    __pool:redis.ConnectionPool = None
    def __init__(self,host,port,db,password):
        '''初始化连接'''
        self.__class__.__pool = redis.ConnectionPool(host=host, port=port, db=db,password=password)
        self.__link = redis.Redis(connection_pool=self.__pool)

    def store(self, alias:str, value, *args, **kwargs) -> bool:
        '''存储数据'''
        return self.__link.set(name=alias, value=value, *args, **kwargs)

    def load(self, alias:str):
        '''加载数据'''
        return self.__link.get(name=alias)

    def store_dataframe(self, alias:str, local_dataframe:pl.DataFrame, *args, **kwargs) -> bool:
        '''存储DataFrame数据类型的缓存'''        
        with BytesIO() as f:
            local_dataframe.write_parquet(f)
            return self.__link.set(name=alias, value=f.getvalue(), *args, **kwargs)

    def load_dataframe(self, alias:str) -> pl.DataFrame:
        '''加载DataFrame数据类型的缓存'''
        with BytesIO(self.__link.get(name=alias)) as f:
            return pl.read_parquet(f)

    def delete(self, *alias:str) -> int:
        '''删除别名对于缓存'''
        return self.__link.delete(*alias)

    def exists(self,*alias:str) -> int:
        '''返回存在的名称数'''
        return self.__link.exists(*alias)
            
    def __del__(self):
        '''自动释放Redis连接'''
        if self.__link:
            self.__link.close()

