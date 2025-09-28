import wrapt
from threading import Thread
import polars as pd


@wrapt.decorator
def new_thread(wrapped, instance, args, kwargs):
    '''装饰器启动新的线程'''
    thread = Thread(target=wrapped,args=args,kwargs=kwargs)
    thread.start()
    return thread.is_alive()

def get_bit_val(byte,index):
    '''获取二进制位数的值
       public | stock | staff | super | 
    '''
    if int(byte) & (1<<index-1):
        return 1
    else:
        return 0

def bit_list(value):
    '''二进制列表'''
    while value:
        yield value%2
        value = value//2

def bit_series(value):
    """二进制列"""
    return pd.Series(bit_list(value))