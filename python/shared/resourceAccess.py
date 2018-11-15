import redis
import json
from creds import credential

class FetchRedis(object):
    """ Get current price of from Redis"""

    def __init__(self):
        # put this in the config file....
        connect = credential.redisCredential
        self.red = redis.Redis(host=connect['host'], port=connect['port'], password=connect['password'])

    def currentDict(self, key):
        """
        :return the raw object recieved
        """
        res = str(self.red.get(key), 'utf-8')
        return (json.loads(res))

    def fetchValue(self, key):
        dict = self.currentDict(key)
        return (dict)

    def sendValue(self, key, value):
        return (self.red.set(key, value))


f = FetchRedis()