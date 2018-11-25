import redis
import json
import credential
import collections

class TransmitRedis(object):

    def __init__(self, credentials, destKey, fieldsStr=None, chunkCount=None):
        """
       Write dict to Redis based upon the destKey.
       If the objectFieldKey True, then the dest key
       will be extracted from the outDict before it's
       transmitted.

       FieldsStr only applies to dict anything else being generated will
       result in a runtime error.
        :param credentials: redis credentials
        :param destKey: redis path
        :param fieldsStr: comm separated list of fields to send if None, send them all.
        :param chunkCount: previous - 1 tuples to send with the arrival of each new tuple,
        """
        self.credentials = credentials
        self.destKey = destKey
        self.fieldsStr = None
        self.chunkCount = chunkCount

        if fieldsStr is not None:
            self.fieldsStr = fieldsStr.split(",")
            print("Redis destination:", destKey, "fields specified:", self.fieldsStr )
        self.redisHandle = None

    def __enter__(self):
        self.redisHandle = redis.Redis(host=self.credentials['host'],
                                       port=self.credentials['port'],
                                       password=self.credentials['password'])
        if self.chunkCount is not None:
            self.chunk = collections.deque(maxlen=self.chunkCount)
        return(self)

    def __call__(self, sendDict):
        sendData = sendDict
        if self.fieldsStr is not None:
            sendData = {k: sendDict[k] for k in self.fieldsStr}
        if self.chunkCount is not None:
            self.chunk.append(sendData)
            sendData = list(self.chunk)
        self.redisHandle.set(self.destKey, json.dumps(sendData))

    def __exit__(self, type, value, traceback):
        return False

if __name__ == '__main__':
    with TransmitRedis(credential.redisCredential, "/score/bluewater", chunkCount=10) as trans:
        lst = list()
        for idx in range(10):
            trans({"idx":idx, "idxString":"idx_"+str(idx)})


