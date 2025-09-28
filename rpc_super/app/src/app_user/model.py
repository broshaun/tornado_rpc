from src.model import PgSQL
from utils.suger.middle import Rsp,JWT
from config import DB


class SuperM(PgSQL):
     
    def __init__(self, table: str):
        self.session = DB.session
        hpsql = self.set_config(Postgres=DB.postgres).open(schema='super', table=table)
        if hpsql.uid == 0:
            pass
        elif not self.session.exists(f"{self.alias}"):
            Rsp.sign_fail()
        



