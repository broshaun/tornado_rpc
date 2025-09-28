from  utils.suger.middle import Rsp,JWT,RqsH
from .server import RegisterS


class RegisterV(RqsH):

    @Rsp.response
    @JWT.jwt_sign_auth
    def post(self,**argument):
        """用户注册"""
        css = RegisterS()
        css.create(**argument)

    @Rsp.response
    @JWT.jwt_sign_auth
    def delete(self,**argument):
        """用户删除"""
        css = RegisterS()
        css.delete(**argument)
    
    @Rsp.response
    @JWT.jwt_sign_auth
    def put(self,**argument):
        """用户修改"""
        css = RegisterS()
        css.modify(**argument)

    @Rsp.response
    @JWT.jwt_sign_auth
    def get(self,**argument):
        """注册用户查看"""
        css = RegisterS()
        css.browse(**argument)

    @Rsp.response
    @JWT.jwt_sign_auth
    def options(self,**argument):
        """用户信息"""
        css = RegisterS()
        css.find(**argument)


