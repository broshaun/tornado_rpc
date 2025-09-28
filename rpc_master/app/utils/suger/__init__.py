import wrapt
from threading import Thread


@wrapt.decorator
def new_thread(wrapped, instance, args, kwargs):
    '''装饰器启动新的线程'''
    thread = Thread(target=wrapped,args=args,kwargs=kwargs)
    thread.start()
    return thread.is_alive()