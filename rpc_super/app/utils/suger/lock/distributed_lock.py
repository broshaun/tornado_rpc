import redis
import uuid
import time
from typing import Optional, Callable, Union
import threading
from utils.helper.db.buffer import RedisDB

from contextvars import ContextVar



class DistributedLock:
    """通用的Redis分布式锁实现"""
    __lock = ContextVar('lock_key')

    def __init__(self,redis_client:RedisDB):
        self.redis_client = redis_client
   
    
    def set_lock_key(self,lock_key):
        self.lock_key = lock_key
        self.lock_value = str(uuid.uuid4())


    def acquire(self) -> bool:
        """
        获取分布式锁
        :param expire_seconds: 锁的过期时间，防止死锁
        :param retry_times: 获取锁失败时的重试次数
        :param retry_interval: 重试间隔时间(秒)或返回间隔时间的函数
        :return: 是否成功获取锁
        """
        for i in range(4):
            # 使用SET NX命令尝试获取锁，确保原子性
            result = self.redis_client.store(self.lock_key, self.lock_value, nx=True, ex=10)
            if result:
                self.__lock.set(f'{self.lock_key}:{self.lock_value}')
                return True
            
            # 未获取到锁，检查是否需要重试
            if i < 4:
                # 如果是函数，则调用函数获取间隔时间，否则使用固定间隔
                time.sleep(0.1)
        
        # 重试次数耗尽仍未获取到锁
        return False
    
    def release(self) -> bool:
        """
        释放分布式锁，确保只能释放自己获取的锁
        :return: 是否成功释放锁
        """
        # 检查当前线程是否持有锁
        lock = self.__lock.get()
        if not lock:
            return False
        self.redis_client.delete()
        self.__lock.set('')
        return True
    


    
    def with_lock(self, 
                  resource: str, 
                  func: Callable, 
                  *args, 
                  **kwargs) -> Optional[any]:
        """
        上下文管理器风格的锁使用方法
        
        :param resource: 要锁定的资源名称
        :param func: 需要在锁保护下执行的函数
        :param args: 函数参数
        :param kwargs: 关键字参数，可包含expire_seconds, retry_times, retry_interval
        :return: 函数执行结果
        """
        # 从kwargs中提取锁参数，使用默认值如果未提供
        expire_seconds = kwargs.pop('expire_seconds', 10)
        retry_times = kwargs.pop('retry_times', 3)
        retry_interval = kwargs.pop('retry_interval', 0.1)
        
        # 获取锁
        if not self.acquire(resource, expire_seconds, retry_times, retry_interval):
            print(f"无法获取资源 {resource} 的锁，执行函数失败")
            return None
        
        try:
            # 执行受保护的函数
            return func(*args, **kwargs)
        finally:
            # 确保锁会被释放
            self.release()
    
    def __enter__(self):
        """上下文管理器进入方法，不建议直接使用，推荐使用with_lock方法"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出方法，确保锁释放"""
        if self.is_held():
            self.release()
        return False  # 不抑制异常


# 使用示例
if __name__ == "__main__":
    # 初始化分布式锁
    lock_manager = DistributedLock()
    
    # 示例1：保护商品库存更新
    def update_goods_stock(goods_id: str, quantity: int) -> bool:
        print(f"更新商品 {goods_id} 的库存，减少 {quantity} 个")
        time.sleep(0.5)  # 模拟处理时间
        print(f"商品 {goods_id} 库存更新完成")
        return True
    
    # 使用with_lock方法
    result = lock_manager.with_lock(
        resource="goods:123",  # 资源名称，格式可以自定义
        func=update_goods_stock,
        goods_id="123",
        quantity=2,
        expire_seconds=5
    )
    
    # 示例2：保护订单创建
    def create_order(order_id: str) -> str:
        print(f"创建订单 {order_id}")
        time.sleep(0.3)  # 模拟处理时间
        print(f"订单 {order_id} 创建完成")
        return f"order_{order_id}_success"
    
    result = lock_manager.with_lock(
        resource="order:456",
        func=create_order,
        order_id="456",
        expire_seconds=3
    )
    
    # 示例3：直接使用acquire/release
    if lock_manager.acquire(resource="payment:789", expire_seconds=5):
        try:
            print("处理支付 789...")
            time.sleep(0.4)
            print("支付处理完成")
        finally:
            lock_manager.release()
