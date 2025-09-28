import redis
import uuid
import time
from typing import Optional, Callable, Union
import threading

class DistributedReadWriteLock:
    """基于Redis的分布式读写锁实现，支持多读单写"""
    
    def __init__(self, 
                 redis_client: Optional[redis.Redis] = None,
                 redis_host: str = 'localhost', 
                 redis_port: int = 6379, 
                 redis_db: int = 0,
                 lock_prefix: str = 'rw_lock:'):
        """
        初始化分布式读写锁
        
        :param redis_client: 已有的Redis客户端实例
        :param redis_host: Redis服务器主机地址
        :param redis_port: Redis服务器端口
        :param redis_db: Redis数据库编号
        :param lock_prefix: 锁的键前缀
        """
        if redis_client:
            self.redis_client = redis_client
        else:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
        
        self.lock_prefix = lock_prefix
        self.local = threading.local()  # 线程本地存储
        # 初始化线程本地变量
        self.local.reader_count = 0
        self.local.write_lock_acquired = False
        self.local.lock_value = None
    
    def _get_read_lock_key(self, resource: str) -> str:
        """生成读锁键名"""
        return f"{self.lock_prefix}{resource}:read"
    
    def _get_write_lock_key(self, resource: str) -> str:
        """生成写锁键名"""
        return f"{self.lock_prefix}{resource}:write"
    
    def acquire_read(self, 
                    resource: str, 
                    expire_seconds: int = 10, 
                    retry_times: int = 3, 
                    retry_interval: Union[float, Callable] = 0.1) -> bool:
        """
        获取读锁
        
        :param resource: 要锁定的资源名称
        :param expire_seconds: 锁的过期时间
        :param retry_times: 获取锁失败时的重试次数
        :param retry_interval: 重试间隔时间(秒)或返回间隔时间的函数
        :return: 是否成功获取锁
        """
        # 如果当前线程已经持有读锁，直接增加计数
        if self.local.reader_count > 0:
            self.local.reader_count += 1
            return True
            
        read_key = self._get_read_lock_key(resource)
        write_key = self._get_write_lock_key(resource)
        lock_value = str(uuid.uuid4())
        
        for attempt in range(retry_times + 1):
            # 检查是否有写锁，没有则获取读锁
            # 使用Lua脚本确保操作原子性
            lua_script = """
            if redis.call('exists', KEYS[2]) == 0 then
                redis.call('incr', KEYS[1])
                redis.call('expire', KEYS[1], ARGV[1])
                return 1
            else
                return 0
            end
            """
            
            result = self.redis_client.eval(
                lua_script,
                2,  # 键的数量
                read_key, write_key,
                expire_seconds
            )
            
            if result == 1:
                self.local.reader_count = 1
                self.local.lock_value = lock_value
                return True
            
            # 未获取到锁，检查是否需要重试
            if attempt < retry_times:
                interval = retry_interval() if callable(retry_interval) else retry_interval
                time.sleep(interval)
        
        return False
    
    def acquire_write(self, 
                     resource: str, 
                     expire_seconds: int = 10, 
                     retry_times: int = 3, 
                     retry_interval: Union[float, Callable] = 0.1) -> bool:
        """
        获取写锁
        
        :param resource: 要锁定的资源名称
        :param expire_seconds: 锁的过期时间
        :param retry_times: 获取锁失败时的重试次数
        :param retry_interval: 重试间隔时间(秒)或返回间隔时间的函数
        :return: 是否成功获取锁
        """
        # 如果当前线程已经持有写锁，直接返回True
        if self.local.write_lock_acquired:
            return True
            
        read_key = self._get_read_lock_key(resource)
        write_key = self._get_write_lock_key(resource)
        lock_value = str(uuid.uuid4())
        
        for attempt in range(retry_times + 1):
            # 检查是否有读锁或写锁，都没有则获取写锁
            # 使用Lua脚本确保操作原子性
            lua_script = """
            if redis.call('exists', KEYS[1]) == 0 and redis.call('exists', KEYS[2]) == 0 then
                redis.call('set', KEYS[2], ARGV[2], 'NX', 'EX', ARGV[1])
                return 1
            else
                return 0
            end
            """
            
            result = self.redis_client.eval(
                lua_script,
                2,  # 键的数量
                read_key, write_key,
                expire_seconds, lock_value
            )
            
            if result == 1:
                self.local.write_lock_acquired = True
                self.local.lock_value = lock_value
                return True
            
            # 未获取到锁，检查是否需要重试
            if attempt < retry_times:
                interval = retry_interval() if callable(retry_interval) else retry_interval
                time.sleep(interval)
        
        return False
    
    def release_read(self) -> bool:
        """释放读锁"""
        if self.local.reader_count <= 0:
            return False
            
        # 减少读锁计数
        self.local.reader_count -= 1
        
        # 如果是最后一个读锁持有者，删除读锁键
        if self.local.reader_count == 0:
            # 获取所有可能的读锁键（实际使用时应跟踪具体资源）
            # 这里简化处理，实际应用中应存储当前持有的资源信息
            for key in self.redis_client.keys(f"{self.lock_prefix}*:read"):
                self.redis_client.decr(key)
                # 如果计数为0，删除键
                if int(self.redis_client.get(key) or 0) <= 0:
                    self.redis_client.delete(key)
            
            self.local.lock_value = None
        
        return True
    
    def release_write(self) -> bool:
        """释放写锁"""
        if not self.local.write_lock_acquired or not self.local.lock_value:
            return False
        
        # 获取所有可能的写锁键
        for key in self.redis_client.keys(f"{self.lock_prefix}*:write"):
            # 使用Lua脚本确保释放锁的原子性
            lua_script = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """
            
            self.redis_client.eval(
                lua_script,
                1,
                key,
                self.local.lock_value
            )
        
        self.local.write_lock_acquired = False
        self.local.lock_value = None
        return True
    
    def with_read_lock(self, 
                      resource: str, 
                      func: Callable, 
                      *args, 
                      **kwargs) -> Optional[any]:
        """
        带读锁执行函数
        
        :param resource: 资源名称
        :param func: 要执行的函数
        :param args: 函数参数
        :param kwargs: 关键字参数
        :return: 函数执行结果
        """
        expire_seconds = kwargs.pop('expire_seconds', 10)
        retry_times = kwargs.pop('retry_times', 3)
        retry_interval = kwargs.pop('retry_interval', 0.1)
        
        if not self.acquire_read(resource, expire_seconds, retry_times, retry_interval):
            print(f"无法获取资源 {resource} 的读锁，执行函数失败")
            return None
        
        try:
            return func(*args, **kwargs)
        finally:
            self.release_read()
    
    def with_write_lock(self, 
                       resource: str, 
                       func: Callable, 
                       *args, 
                       **kwargs) -> Optional[any]:
        """
        带写锁执行函数
        
        :param resource: 资源名称
        :param func: 要执行的函数
        :param args: 函数参数
        :param kwargs: 关键字参数
        :return: 函数执行结果
        """
        expire_seconds = kwargs.pop('expire_seconds', 10)
        retry_times = kwargs.pop('retry_times', 3)
        retry_interval = kwargs.pop('retry_interval', 0.1)
        
        if not self.acquire_write(resource, expire_seconds, retry_times, retry_interval):
            print(f"无法获取资源 {resource} 的写锁，执行函数失败")
            return None
        
        try:
            return func(*args, **kwargs)
        finally:
            self.release_write()


# 使用示例
if __name__ == "__main__":
    rw_lock = DistributedReadWriteLock()
    
    # 读操作示例
    def read_resource(resource_id):
        print(f"读取资源 {resource_id}...")
        time.sleep(1)  # 模拟读取操作
        print(f"读取资源 {resource_id} 完成")
        return f"resource_{resource_id}_data"
    
    # 写操作示例
    def write_resource(resource_id, data):
        print(f"写入资源 {resource_id}: {data}")
        time.sleep(1)  # 模拟写入操作
        print(f"写入资源 {resource_id} 完成")
        return True
    
    # 测试读锁 - 可以同时进行多个读操作
    def test_readers():
        for i in range(3):
            rw_lock.with_read_lock(
                resource="doc:123",
                func=read_resource,
                resource_id="123",
                expire_seconds=10
            )
    
    # 测试写锁 - 独占资源
    def test_writer():
        rw_lock.with_write_lock(
            resource="doc:123",
            func=write_resource,
            resource_id="123",
            data="new_content",
            expire_seconds=10
        )
    
    # 模拟并发读
    import threading
    threads = []
    for _ in range(3):
        t = threading.Thread(target=test_readers)
        threads.append(t)
        t.start()
    
    # 等待所有读线程完成
    for t in threads:
        t.join()
    
    # 执行写操作
    test_writer()
