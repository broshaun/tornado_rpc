from .setting import WebIP
from .setting import Times
from .dbase import RPCServer




## 测试运行
# RPCServer().store('super','tcp://192.168.64.1:4242') ## 这句在微服务正常部署，并将微服务地址写入redis就可以不要运行，仅用于测试

class RPC:
    '''微服务读取地址'''
    @classmethod
    def get_rpcserver(cls,rpcserver:str):
        endpoint = RPCServer().load(rpcserver)
        if isinstance(endpoint, bytes):
            endpoint = endpoint.decode('utf-8')
        return endpoint
        


## 调试模式True/False
DEBUG = True