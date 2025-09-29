from utils.helper.db.pgsql import DBOpen
from utils.helper.db.buffer import RedisDB




class BliDB():
    HOST = "postgres.service"
    PORT = 5432
    DBUSER = "postgres"
    DBPWD = "su7vu9xyzl0bzrur5jq"
    DBNAME = "postgres"
    def __new__(cls):
        return DBOpen(host=cls.HOST,port=cls.PORT,user=cls.DBUSER,password=cls.DBPWD,database=cls.DBNAME)


class Session:
    HOST = "redis.service"
    DBPWD = "su7vu9xyzl0bzrur5jq"
    PORT = 6379
    DB = 3
    def __new__(cls):
        return RedisDB(host=cls.HOST,port=cls.PORT,db=cls.DB,password=cls.DBPWD)


class RPCServer:
    HOST = "redis.service"
    DBPWD = "su7vu9xyzl0bzrur5jq"
    PORT = 6379
    DB = 6
    def __new__(cls):
        return RedisDB(host=cls.HOST,port=cls.PORT,db=cls.DB,password=cls.DBPWD)



