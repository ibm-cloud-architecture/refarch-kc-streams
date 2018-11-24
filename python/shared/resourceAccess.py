import redis
import json
import credential

class TransmitRedis(object):

    def __init__(self, credentials, destKey, fieldsStr=None):
        """
       Write dict to Redis based upon the destKey.
       If the objectFieldKey True, then the dest key is
       will be extracted from the outDict before it's
       transmitted - this giving you 'dynamic' keys.
        :param credentials: redis credentials
        :param destKey: redis path
        :param fieldsStr: comm separated list of fields to send if None, send them all.
        """

        self.credentials = credentials
        self.destKey = destKey
        self.fieldsStr = None
        if fieldsStr is not None:
            self.fieldsStr = fieldsStr.split(",")
            print("Redis destination:", destKey, "fields specified:", self.fieldsStr )
        self.redisHandle = None



    def __enter__(self):
        self.redisHandle = redis.Redis(host=self.credentials['host'],
                                       port=self.credentials['port'],
                                       password=self.credentials['password'])
    def __exit__(self):
        # if you have __enter__() you must have __exit__()
        pass

    def __call__(self, outDict ):
        sendDict = outDict
        if self.fieldsStr is not None:
            sendDict = {k: outDict[k] for k in self.fieldsStr}

        self.redisHandle.set(self.destKey, json.dumps(sendDict))


if __name__ == '__main__':
    transmit = TransmitRedis(credential.redisCredential, "/score/control")
    for idx in range(10):
        transmit({"idx":idx, "idxString":"idx_"+str(idx)})