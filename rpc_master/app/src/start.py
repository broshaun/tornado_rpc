import asyncio
from tornado.web import Application
from utils.suger.middle import RqsH
from config import WebIP
from src.views import RPCViews



class Hello(RqsH):
    def get(self):
        self.write("Hello Tornado!!!")

def make_app():
    return Application([
        (r"/", Hello),
        (r"/([^/]+)/(.*)", RPCViews),
    ])


async def run():


    print(f"启动web服务 http://{WebIP.HOST}:{WebIP.PORT}")
    app = make_app()
    app.listen(WebIP.PORT,WebIP.HOST)
    await asyncio.Event().wait()


