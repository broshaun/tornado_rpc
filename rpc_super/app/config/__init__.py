from .dbase import BliDB,Session,RPCServer
from .setting import TCP,Times
from utils.helper import new_thread
import time

class DB:
    postgres = BliDB()
    session = Session()



class RPC:
    @new_thread
    @classmethod
    def set_super(cls,seconds=10):
        while 1:
            RPCServer().store('super',f'tcp://{TCP.HOST}:{TCP.PORT}')
            print(f"Redis设定rpc_super[tcp://{TCP.HOST}:{TCP.PORT}]")
            time.sleep(seconds)

RPC.set_super()


## 调试模式True/False
DEBUG = True