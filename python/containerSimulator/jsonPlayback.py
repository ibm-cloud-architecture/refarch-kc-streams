"""
Streams Application * Simulate a containers' and ships.

Data pushed across onto message hub.

The data file records that look like:
 {
    "tempC": 8.381110706248602,
    "amp": 0.0,
    "latitude": 5.096282982,
    "id": "Reefer_6",
    "oTemp": 17.8,
    "ts": "2018-01-04 01:54:00",
    "longitude": 95.16426085
  },

 Split these into two separate MH streams:



"""

import common

from pathlib import Path
import time
import datetime
import argparse

import streamsx.messagehub as messagehub

import credential
from streamsx.topology.topology import *
from streamsx.topology.schema import *
import streamsx.ec




def read_data(input_file):
    """
    Read the data from the file that was packed in the sag.
    """
    with open(input_file, 'r') as input_file:
        data_raw = json.load(input_file)
    return data_raw

class FileFeed(object):
    def __init__(self, filename, intermessageWait=.2):
        """
        Provide a feed of patient ekg data, recycles when the end of data is reached.
        :param filename: filename of json - no path info.
        :param intermessageWait: time to wait between messages
        """
        self.filename = filename
        self.data = None
        self.waitPeriod = intermessageWait

    def __iter__(self):
        return self

    def __enter__(self):
        fullFilePath = os.path.join(streamsx.ec.get_application_directory(), 'etc', self.filename)
        self.data = read_data(fullFilePath)
        self.datalen = len(self.data)
        self.idx = 0

    def __exit__(self, exc_type, exc_value, traceback):
        """required if you have __enter__()"""
        pass


    def __next__(self):
        if self.idx >= self.datalen:
            ts = time.time()
            print("Resetting index @ ", datetime.datetime.fromtimestamp(ts).isoformat() )
            self.idx = 0
        chunk  = self.data[self.idx]
        self.idx += 1
        time.sleep(self.waitPeriod)
        return(chunk)

def shipData(iDict):
    nDict = dict(iDict)
    nDict['shipId'] = "medusa"
    [nDict.pop(k, None) for k in ('amp', 'tempC', 'oTemp', 'id')]
    return nDict

def containerData(iDict):
    nDict = dict(iDict)
    nDict['shipId'] = "medusa"
    nDict['containerId'] = iDict['id']
    [nDict.pop(k, None) for k in ('latitude','longitude','id','oTemp')]
    return nDict



def json2FileHub(jobName, nameSpace, mhTopic, jsonDataPath, message_wait):
    topo = Topology(jobName, nameSpace)

    # Add the file to the sab so it will be in etc when deployed
    topo.add_file_dependency(jsonDataPath, "etc")
    jsonDataFile = os.path.basename(jsonDataPath)
    print(jsonDataFile)
    allEvents = topo.source(FileFeed(filename=jsonDataFile, intermessageWait=message_wait))

    shipStream = allEvents.map(shipData, name="shipData")
    containerStream = allEvents.map(containerData, name="containerData")

    shipJson = shipStream.as_json(name="shipJson")
    containerJson = containerStream.as_json(name="containerJson")

    messagehub.publish(shipJson, topic="bluewaterShip", name="shipMH")
    messagehub.publish(containerJson, topic="bluewaterContainer", name="containerMH")
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
    # application specfic arguments...
    parser.add_argument('--mhTopic', help="MessageHub topic to to send ekg events out on.", default="jsonEvents")
    parser.add_argument('--jsonData', help="Json data file, list of records to push ", default="reeferTrack.json")
    parser.add_argument('--messageWait', help="Subsecond time to wait between transmitting data", default="0.2")

    args = parser.parse_args()
    print("resolved args:", args)
    topo = json2FileHub(jobName=args.jobName, nameSpace=args.nameSpace,
                       mhTopic=args.mhTopic,
                       jsonDataPath=args.jsonData,
                       message_wait=float(args.messageWait))

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
          cancel=args.cancel )
    print("Process status:%s" % submitStatus)



