import common
import credential

import numpy as np
from streamsx.topology.topology import *
from streamsx.topology.schema import *
import streamsx.messagehub as messagehub
from pathlib import Path

import struct
import time
import datetime
import argparse


def read_ekg_data(input_file):
    """
    Read the EKG data from the file.
    """
    print("read_ekg", flush=True)
    with open(input_file, 'rb') as input_file:
        data_raw = input_file.read()
    n_bytes = len(data_raw)
    n_shorts = n_bytes/2
    # data is stored as 16-bit samples, little-endian
    # '<': little-endian
    # 'h': short
    unpack_string = '<%dh' % n_shorts
    # sklearn seems to throw up if data not in float format
    data_shorts = np.array(struct.unpack(unpack_string, data_raw)).astype(float)
    print(data_shorts, flush=True)
    return [int(ele) for ele in data_shorts]


def jsonMsg(patientId, chunk):
    ts = time.time()
    msg = json.dumps({"pid": str(patientId), "ts": ts, "ekg": chunk})
    return msg

class SimFeed(object):
    """replay data feed"""
    def __init__(self,patiendId,filename, samplesPerSecond=100):
        """
        Provide a feed of patient ekg data, recycles when the end of data is reached.
        :param patiendId:
        :param filename: with ekg data
        :param samplesPerSecond:
        """
        self.id = patiendId
        self.filename = filename
        self.data = None
        self.samplesPerSecond = samplesPerSecond

    def __iter__(self):
        return self

    def __enter__(self):
        fullFilePath = os.path.join(streamsx.ec.get_application_directory(), 'etc', self.filename)
        self.data = read_ekg_data(fullFilePath)
        self.datalen =  len(self.data)
        print("Start data len:", self.datalen )
        self.idx = 0

    def __exit__(self):
        """required if you have __enter__()"""
        pass

    def __next__(self):
        if ((self.idx + self.samplesPerSecond) >= self.datalen):
            ts = time.time()
            print("Resetting index @ ", datetime.datetime.fromtimestamp(ts).isoformat() )
            self.idx = 0


        extent = self.idx+self.samplesPerSecond
        chunk  = self.data[self.idx:extent]
        self.idx = extent
        time.sleep(1.0)
        return jsonMsg(self.id, chunk)



def EkgOutHub(jobName, nameSpace, ekgTopic):
    topo = Topology(jobName, nameSpace)

    topo.add_file_dependency('data/patients/a02.dat', "etc")

    # configuration in StreamsConsole : https://streamsxmessagehub.readthedocs.io/en/pypackage

    to_mh = topo.source(SimFeed(patiendId="a02.dat",filename="a02.dat"))
    to_mh = to_mh.as_string()
    to_mh.print(name="print")


    # Publish a stream to Message Hub
    messagehub.publish(to_mh, topic=ekgTopic)
    return topo




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build & Deploy EKG data ')
    parser.add_argument('--pwd', help="password to decrypyt credential file", default=None)
    parser.add_argument('--streamsService', help="Name of the Streams Analytics service", default="Streaming3Turbine")
    parser.add_argument('--serviceType', help="Type of service to build: STREAMING_ANALYTICS, BUILD_ARCHIVE.", default="STREAMING_ANALYTICS")
    parser.add_argument('--buildType',
                        help="Either 'DISTRIBUTED' or 'BUNDLE' determines if scripts+submit or just scripts.",
                        default="DISTRIBUTED")
    defJobName = Path(parser.prog).resolve().stem
    parser.add_argument('--jobName', help="Name to assign to the job name", default=defJobName)
    parser.add_argument('--nameSpace', help="Name to assign to the namespace", default=defJobName)
    parser.add_argument('--cancel', help="Cancel active job before submitting job, uses jobName, nameSpace", default=True)
    ## application specfic arguments...
    parser.add_argument('--ekgTopic', help="MessageHub topic to to send ekg events out on.", default="ekgEvents")

    args = parser.parse_args()

    topo = EkgOutHub(jobName=args.jobName, nameSpace=args.nameSpace, ekgTopic=args.ekgTopic)

    try:
        import creds.credential as creds
    except ImportError:
        common.decryptCredentials(zipPath="../shared/creds/", cryptFile="credential.py.zip", decryptFile='credential.py', pwd=args.pwd)
        import creds.credential as creds
    submitStatus = common.submitProcess(topology=topo,
          streamsService=args.streamsService,
          buildType=args.buildType,
          serviceType=args.serviceType,
          jobName=args.jobName,
          cancel=args.cancel)
    print("Process status:%s" % submitStatus)



