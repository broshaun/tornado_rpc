from datetime import datetime,timedelta
from contextvars import ContextVar
import wrapt
import jwt
from jwt.exceptions import *
import os
from .answer import Rsp


class JWT:
    '''上下文变量:
    Usr 当前会话用户标识
    用户认证
    '''
    SECRET_KEY = os.urandom(24)
    Usr = ContextVar('User',default={})

    @classmethod
    def get_user(cls):
        '''获取user
        { 
            uid : 用户标示,
            sub : 面向用户, 比如: super、client、customer,
            eff : 有效时间-秒
        }
        '''
        return cls.Usr.get()    
    
    @wrapt.decorator
    @classmethod
    def jwt_sign_auth(cls,wrapped, instance, args, kwargs):
        'JWT签名认证'
        if instance.token:
            cls.Usr.set(cls.jwt_decode(instance.token))
        return wrapped(*args, **kwargs)

    @classmethod
    def jwt_login(cls,uid:int,sub,eff:int):
        ''' 登陆:
        uid 用户标示
        sub 面向用户, 比如: super、client、customer
        eff 有效时间-秒
        '''
        payload = {
            'uid': int(uid),
            'sub': sub,
            'exp': datetime.now() + timedelta(seconds=int(eff)),  # 过期时间-秒
            }
        token = jwt.encode(payload,cls.SECRET_KEY,algorithm='HS256')
        return token

    @classmethod
    def jwt_refresh(cls,uid:int,eff:int):
        ''' 刷新:
        uid 用户标示
        eff 有效时间-秒
        '''
        payload = {
            'uid': int(uid),
            'sub': 'refresh',
            'exp': datetime.now() + timedelta(seconds=int(eff)),  # 过期时间
            }
        token = jwt.encode(payload,cls.SECRET_KEY,algorithm='HS256')
        return token

    @classmethod
    def jwt_decode(cls,token:str):
        ''' 解码:
        token 用户标示
        '''
        try:
            return jwt.decode(token, cls.SECRET_KEY, algorithms=['HS256'])
        except  ExpiredSignatureError:
            Rsp.invalid_token(data="Token已过期")
        except InvalidTokenError as e:
            Rsp.invalid_token(data="验证不通过")