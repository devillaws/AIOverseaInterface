import threading
lock = threading.Lock()

key_times = {
    "123": 0,
    "456": 0,
    "789": 0
}

key_time_deque = {

}



def update_key_times():
    global key_times
    # 在修改全局变量之前，获取锁
    lock.acquire()
    try:
        # 修改全局变量
        pass
    finally:
        # 释放锁
        lock.release()

def update_key_time_deque():
    global key_time_deque
    # 在修改全局变量之前，获取锁
    lock.acquire()
    try:
        # 修改全局变量
        pass
    finally:
        # 释放锁
        lock.release()
