from utils.suger.middle import Rsp
import json
import aiozmq.rpc
from aiozmq.rpc import Error,NotFoundError,ParametersError,ServiceClosedError,GenericError



class RPClient():
    '''RPC客户端，用于与RPC服务端通信'''
    def __init__(self,rpcserver):
        if not rpcserver:
            Rsp.rpc(msg=f'未设定RPCServer地址:[{rpcserver}]')
        self.rpcserver = rpcserver

    async def run(self, path:str,method:str,token:str,kwargs:dict):
        """调用RPC服务端的echo方法
        
        Args:
            path: 路径参数
            method: 方法名 这里就是后续访问的 get | post | put ... 方法
            token: 身份验证令牌
            kwargs: 传递的关键字参数
        
        """
        client = None
        try:
            # 连接RPC服务端
            client = await aiozmq.rpc.connect_rpc(connect=self.rpcserver)
            # 调用服务端的echo方法
            result = await client.call.echo(path,method,token,kwargs)
            # 处理返回结果
            if isinstance(result,dict): 
                Rsp.customize(result.get('code'),result.get('message'),json.loads(result.get('data')))
            else:
                Rsp.no_content(msg=f'RPCServer[{self.rpcserver}]未按指定格式返回',data=result)
        except NotFoundError as e:
            Rsp.rpc(msg=f"NotFoundError: [{self.rpcserver}]不存在echo方法。")
        except ParametersError as e:
            Rsp.rpc(msg=f'ParametersError: [{self.rpcserver}]调用echo方法时参数不匹配。')
        except ServiceClosedError as e:
            Rsp.rpc(msg=f'ServiceClosedError: [{self.rpcserver}]服务已关闭。')
        except GenericError as e:
            data = {}
            data['异常类型'] = e.exc_type
            data['异常参数'] = e.arguments
            data['异常详情：'] = e.exc_repr
            Rsp.rpc(msg=f"GenericError: [{self.rpcserver}]服务未定义异常", data=data)
        except Error as e:
            Rsp.rpc(msg=f"Error: RPC调用发生未知错误 {str(e)}")
        except Exception as e:
            Rsp.rpc(msg=f"RPClientError: {e}")
        finally:
            if client:
                client.close()

        
    
