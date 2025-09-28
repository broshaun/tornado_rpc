from tornado.web import RequestHandler
from tornado.escape import json_decode


class RqsH(RequestHandler):
    '''请求处理基类'''
    def prepare(self):
        self.kwargs = {}
        self.token = self.request.headers.get('Authorization','')
        self.method = self.request.method
        content_type:str = self.request.headers.get('content-type','')
        if content_type.startswith('application/json'):
            self.kwargs = json_decode(self.request.body)
        else:
            for key in self.request.arguments:
                self.kwargs[key] = self.get_argument(key)
