from utils.suger.middle import Routes
from src import app_user
from config import TCP,DEBUG
import asyncio
from aiozmq import rpc


class Views(Routes):
    def routes_set(self):
        self.routes[r'login/'] = app_user.LoginV
        self.routes[r'register/'] = app_user.RegisterV

async def start_server():
    """启动RPC服务端"""
    server = await rpc.serve_rpc(Views(), bind=f"tcp://*:{TCP.PORT}")
    print(f"RPC服务端启动, 监听端口 {TCP.PORT} ...")
    await server.wait_closed()  # 保持服务运行（等待关闭信号）



if __name__ == "__main__":
    if DEBUG:
        print('当前为调试模式 ...')
    else:
        print('当前为线上模式 ...')
    asyncio.run(start_server())
