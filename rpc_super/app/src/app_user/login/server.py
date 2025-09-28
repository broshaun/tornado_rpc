from utils.suger.middle import Rsp,JWT
from src.app_user.model import SuperM


class LoginS():
    """用户登陆"""
    def __init__(self):
        
        self.obj = SuperM(table='user')
 
    def sign_in(self,email,pass_word):
        '''用户登陆'''
        sqltext = """
        select "id","phone","pass_word",100000 as expired,'super' as roles
        from "super"."user" 
        where is_delete IS FALSE AND "email" = %(email)s
        """
        for ss in self.obj.bysql(sqltext,where={"email":email}).iter_rows(named=True):
            if pass_word == ss['pass_word']:
                self.obj.session.store(alias=f"{ss['roles']}:{ss['id']}",value="1",ex=10000)
                data = {}
                data['login_token'] = JWT.jwt_login(uid=ss['id'],sub=ss["roles"],eff=100000)
                data['login_expired'] = 100000
                data['refresh_token'] = JWT.jwt_refresh(uid=ss['id'], eff=ss['expired'])
                Rsp.ok(data)
        else:
            Rsp.login_fail()
            

    def sign_out(self):
        '''用户登出；清除缓存'''
        Rsp.ok(data=self.obj.session.delete(self.obj.alias),msg="注销成功")


    def sign_new(self,refresh_token):
        '''刷新验证；获取新的Token'''
        data = dict()
        payload = JWT.jwt_decode(refresh_token)
        if payload['sub'] != "refresh":
            Rsp.invalid_token()
        data['login_token'] = JWT.jwt_login(uid=payload["uid"],sub="super",eff=10000)
        data['login_expired'] = 10000
        Rsp.ok(data)
    
    def sign_info(self):
        '登陆信息获取'
        data = dict()
        data = self.obj.byid(self.obj.uid)
        Rsp.ok(data)

    def sign_password(self,pass_word):
        '修改登录密码'
        self.obj.begin()
        self.obj.update(id=self.obj.uid,pass_word=pass_word)
        self.obj.commit()
        Rsp.ok(self.obj.rowcount,msg="密码修改成功")
