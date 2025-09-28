from utils.helper.db import RedB


class  RPCServer:
    HOST = "redis.service"
    DBPWD = "su7vu9xyzl0bzrur5jq"
    PORT = 6379
    DB = 6

    def __new__(cls):
        return RedB(host=cls.HOST,port=cls.PORT,db=cls.DB,password=cls.DBPWD)
    


