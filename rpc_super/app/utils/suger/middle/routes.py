import asyncio
from aiozmq import rpc
from typing import Dict, Callable, Awaitable

class Routes(rpc.AttrHandler):
    '路由基础类'
    
    def __init__(self):
        super().__init__()  # 初始化父类AttrHandler
        self.routes: Dict[str, Callable] = {} # 存储路由映射关系
        self.routes_set() # 注册路由

    def routes_set(self):
        pass
    
    @rpc.method
    async def echo(self,path:str,method:str,token:str,kwargs:dict):
        '''说明：
        执行 fn_method 方法。
        fn_method 的方法也可以是异步的，当返回结果是为执行的 <coroutine object> 则使用 result = await result 执行。
        返回 method 的结果
        '''
        obj = self.routes[path](token)
        fn_method = method.lower()
        if hasattr(obj, fn_method):
            result = getattr(obj, fn_method)(**kwargs) # 执行obj对象的fn_method方法
            if isinstance(result, Awaitable):
                result = await result
            return result    
        
    @rpc.method
    async def test(self,name):
        await asyncio.sleep(5)
        return f'Hello {name}.'








