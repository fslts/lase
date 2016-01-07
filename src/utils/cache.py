import redis

#TODO to config
REDIS_LASE_HOST_PREFIX = 'lase.host.'
REDIS_LASE_HOST_EXPIRE = '1000'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

class LaseRedisCache:

    def __init__(self):
        self._r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def store_host(self, host, ports):
        self._r.set(REDIS_LASE_HOST_PREFIX + host, ports)
        self._r.expire(REDIS_LASE_HOST_PREFIX + host, REDIS_LASE_HOST_EXPIRE)

    def load_host(self, host):
        res = self._r.get(REDIS_LASE_HOST_PREFIX + host)
        if not res:
            return []
        return res
