from utils.suger.middle import Rsp, RqsH
from utils.helper.rpc import RPClient
from config import RPC


class RPCViews(RqsH):

    @Rsp.response
    async def post(self,rpcserver:str,path:str):
        rpclient = RPClient(RPC.get_rpcserver(rpcserver))
        await rpclient.run(path,self.method,self.token,self.kwargs)
 
    @Rsp.response
    async def delete(self,rpcserver:str,path:str):
        rpclient = RPClient(RPC.get_rpcserver(rpcserver))
        await rpclient.run(path,self.method,self.token,self.kwargs)

    @Rsp.response
    async def options(self,rpcserver:str,path:str):
        rpclient = RPClient(RPC.get_rpcserver(rpcserver))
        await rpclient.run(path,self.method,self.token,self.kwargs)


    @Rsp.response
    async def get(self,rpcserver:str,path:str):
        rpclient = RPClient(RPC.get_rpcserver(rpcserver))
        await rpclient.run(path,self.method,self.token,self.kwargs)
        
        
    @Rsp.response
    async def put(self,rpcserver:str,path:str):
        rpclient = RPClient(RPC.get_rpcserver(rpcserver))
        await rpclient.run(path,self.method,self.token,self.kwargs)