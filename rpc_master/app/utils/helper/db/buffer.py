import redis


class RedB():
    __POOL:redis.ConnectionPool = None
    def __init__(self,host,port,db,password):
        '''初始化连接'''
        self.__class__.__POOL = redis.ConnectionPool(host=host, port=port, db=db,password=password)
        self.__link = redis.Redis(connection_pool=self.__POOL)

    def store(self, alias:str, value, *args, **kwargs) -> bool:
        '''存储数据'''
        return self.__link.set(name=alias, value=value, *args, **kwargs)

    def load(self, alias:str):
        '''加载数据'''
        return self.__link.get(name=alias)
    