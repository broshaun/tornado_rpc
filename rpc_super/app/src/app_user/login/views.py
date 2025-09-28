from .server import LoginS
from utils.suger.middle import Rsp,JWT,RqsH
import asyncio



class LoginV(RqsH):

    @Rsp.response
    def post(self,**kwargs):
        '用户登陆'
        css = LoginS()
        css.sign_in(**kwargs)

    @Rsp.response
    @JWT.jwt_sign_auth
    def delete(self,**kwargs):
        '登陆注销'
        css = LoginS()
        css.sign_out(**kwargs)
    
    @Rsp.response
    def options(self,**kwargs):
        '刷新验证'
        css = LoginS()
        css.sign_new(**kwargs)

    @Rsp.response
    @JWT.jwt_sign_auth
    async def get(self,**kwargs):
        '登录信息'
        # import time
        # time.sleep(5) ## 如果使用线程阻塞，会有影响整个rpc服务
        css = LoginS()
       
        await asyncio.sleep(10)
        css.sign_info(**kwargs)

    @Rsp.response
    @JWT.jwt_sign_auth
    def put(self,**kwargs):
        '修改登录密码'
        css = LoginS()
        css.sign_password(**kwargs)
        


