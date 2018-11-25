import redis
import json
import credential
import collections


class TransmitRedis(object):
    def __init__(self, credentials, dest_key, fields_str=None, chunk_count=None):
        """
       Write dict to Redis based upon the destKey.
       If the objectFieldKey True, then the dest key
       will be extracted from the outDict before it's
       transmitted.

       FieldsStr only applies to dict anything else being generated will
       result in a runtime error.
        :param credentials: redis credentials
        :param dest_key: redis path
        :param fields_str: comm separated list of fields to send if None, send them all.
        :param chunk_count: previous - 1 tuples to send with the arrival of each new tuple,
        """
        self.credentials = credentials
        self.destKey = dest_key
        self.fieldsStr = None
        self.chunkCount = chunk_count

        if fields_str is not None:
            self.fieldsStr = fields_str.split(",")
            print("Redis destination:", dest_key, "fields specified:", self.fieldsStr)
        self.redisHandle = None

    def __enter__(self):
        self.redisHandle = redis.Redis(host=self.credentials['host'],
                                       port=self.credentials['port'],
                                       password=self.credentials['password'])
        if self.chunkCount is not None:
            self.chunk = collections.deque(maxlen=self.chunkCount)
        return self

    def __call__(self, send_dct):
        send = send_dct
        if self.fieldsStr is not None:
            send = {k: send_dct[k] for k in self.fieldsStr}
        if self.chunkCount is not None:
            self.chunk.append(send)
            send = list(self.chunk)
        self.redisHandle.set(self.destKey, json.dumps(send))

    def __exit__(self, type, value, traceback):
        return False


if __name__ == '__main__':
    with TransmitRedis(credential.redisCredential, "/score/bluewater", chunk_count=10) as trans:
        lst = list()
        for idx in range(10):
            trans({"idx": idx, "idxString": "idx_"+str(idx)})