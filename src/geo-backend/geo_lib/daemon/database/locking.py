import threading

import redis
from redis.exceptions import LockError


class DBLockManager:
    _redis = redis.Redis(host='localhost', port=6379, db=0)
    locks = {}
    locks_lock = threading.Lock()

    def __init__(self, worker_id):
        self.worker_id = worker_id

    def lock_row(self, table_name: str, primary_key):
        lock = self._redis.lock(f'database_lock_{table_name}:{primary_key}')
        if lock.acquire(blocking=False):
            with self.locks_lock:
                self.locks[f'{table_name}:{primary_key}'] = lock
            return True
        else:
            return False

    def unlock_row(self, table_name: str, primary_key):
        with self.locks_lock:
            lock = self.locks.get(f'{table_name}:{primary_key}')
        if lock:
            try:
                lock.release()
                return True
            except LockError:
                return False
        else:
            return False
