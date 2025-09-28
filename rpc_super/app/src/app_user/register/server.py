from src.app_user.model import SuperM
from utils.suger.middle import Rsp



class RegisterS():
    """子用户管理"""
    def __init__(self):
        self.obj = SuperM(table="user")

    def create(self,email,pass_word):
        if not self.obj.search(where={"email":email}).is_empty():
            Rsp.repeat("邮箱已注册")
        self.obj.begin()
        self.obj.insert(email=email,pass_word=pass_word)
        self.obj.commit()
        Rsp.ok(self.obj.lastid,msg='注册成功。')
    

    def delete(self,id):
        self.obj.begin()
        self.obj.delete(id)
        self.obj.commit()
        Rsp.ok(self.obj.rowcount)

    def modify(self,id,phone=None,email=None,pass_word=None):
        if phone:
    
            if not self.obj.search(where={"phone":phone}).is_empty():
                Rsp.repeat("电话已注册")
        if email:
            if not self.obj.search(where={"email":email}).is_empty():
                Rsp.repeat("邮箱已注册")
        self.obj.begin()
        self.obj.update(id=id,phone=phone,email=email,pass_word=pass_word)
        self.obj.commit()
        Rsp.ok(self.obj.rowcount)

    def find(self,id):
        for ss in self.obj.search(where={"id":id}).iter_rows(named=True):
            Rsp.ok(ss)

    def browse(self,**kwargs):
        "查看子用户"
        sql = """
        SELECT usr.id,usr.phone,usr.email,usr.last_time,usr.create_time
        FROM super.user usr
        WHERE usr.is_delete IS False AND usr.creator = %(uid)s
        """
        kwargs['uid'] = self.obj.uid
        data = self.obj.bysql_for_total_detail(sql,where=kwargs)
        Rsp.ok(data)
            
        
        



