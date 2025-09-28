import asyncio
from src import start as webstart
from config import DEBUG


if __name__ == "__main__":
    if DEBUG:
        print('当前为调试模式 ...')
    else:
        print('当前为线上模式 ...')

    asyncio.run(webstart.run()) 
    