from .hpsql import CRUD
from .dbops import PgDB


class DBOpen(PgDB):
    def open(self,schema,table):
        return CRUD(dbcon=self,schema=schema,table=table)