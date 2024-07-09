import threading

import redis
from redis.exceptions import LockError


def _get_lock_name(table_name: str, primary_key: str):
    return f'database_lock_{table_name}:{primary_key}'


class DBLockManager:
    _redis = redis.Redis(host='localhost', port=6379, db=0)
    locks_lock = threading.Lock()
    _locks = {}

    def __init__(self, worker_id=None):
        self.worker_id = worker_id
        self._read_only = worker_id is None

    def lock_row(self, table_name: str, primary_key):
        if self._read_only:
            raise Exception('Cannot lock row in read-only mode')
        lock_name = _get_lock_name(table_name, primary_key)
        lock = self._redis.lock(lock_name)
        if lock.acquire(blocking=False):
            self._locks[lock_name] = lock
            return True
        return False

    def unlock_row(self, table_name: str, primary_key):
        if self._read_only:
            raise Exception('Cannot unlock row in read-only mode')
        lock_name = _get_lock_name(table_name, primary_key)
        lock = self._locks.get(lock_name)
        if lock is None:
            return False
        try:
            lock.release()
            del self._locks[lock_name]
            return True
        except LockError:
            return False

    def is_locked(self, table_name: str, primary_key):
        return self._redis.lock(_get_lock_name(table_name, primary_key)).locked()
