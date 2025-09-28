from tornado.web import RequestHandler
from asyncio import CancelledError
import wrapt
from typing import Awaitable


class Rsp(CancelledError):
    """
    1**	信息,服务器收到请求,需要请求者继续执行操作
    2**	成功,操作被成功接收并处理
    3**	重定向,需要进一步的操作以完成请求
    4**	客户端错误,请求包含语法错误或无法完成请求
    5**	服务器错误,服务器在处理请求的过程中发生了错误
    """
    def __init__(self,code=0,message='',data=None):
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def customize(cls,code,message,data):
        '自定义返回'
        this = cls(code,message,data)
        raise this
    
    @classmethod
    def ok(cls,data=None,msg=""):
        '请求成功,正常返回。'
        result = {"code": 200,"message": msg,"data":data}
        this = cls(**result)
        raise this

    @classmethod
    def no_content(cls,msg='',data=None):
        '无内容。服务器成功处理,但未返回内容。在未更新网页的情况下,可确保浏览器继续显示当前文档'
        result = {"code": 204, "message": "无内容", "data": data}
        if msg:
            result["message"] = msg
        this = cls(**result)
        raise this
    
    @classmethod
    def invalid_token(cls,msg='',data=None):
        '无效Token'
        result = {"code": 334, "message": "无效Token", "data": data}
        if msg:
            result["message"] = msg
        this = cls(**result)
        raise this
    
    @classmethod
    def rpc(cls,msg='',data=None):
        'rpc服务端错误'
        print("message",msg)
        result = {"code": 502, "message": "rpcserver错误", "data": data}
        if msg:
            result["message"] = msg
        this = cls(**result)
        raise this
    
    @wrapt.decorator
    @classmethod
    async def response(cls,wrapped, instance:RequestHandler, args, kwargs):
        '''返回对应响应信息,拦截异常'''
        from config import DEBUG
        
        result = {}
        try:
            result = wrapped(*args, **kwargs)
            if isinstance(result, Awaitable):
                await result

        except Rsp as s:
            result = {"code": s.code, "message": s.message, "data": s.data}

        except Exception:
            if DEBUG:
                raise
            result = {"code": 500, "message": "服务错误"}

        finally:
            instance.write(result)

        