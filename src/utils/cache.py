import redis

#TODO to config
HOST_PREFIX = 'lase.host.'
HOST_EXPIRE = '1000'

class LaseRedisCache:

    def __init__(self):
        self._r = redis.StrictRedis(host='localhost', port=6379, db=0)

    def store_host(self, host, ports):
        self._r.set(HOST_PREFIX + host, ports)
        self._r.expire(HOST_PREFIX + host, HOST_EXPIRE)

    def load_host(self, host):
        return self._r.get(HOST_PREFIX + host)
