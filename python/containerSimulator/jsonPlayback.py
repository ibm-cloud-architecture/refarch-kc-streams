import common
import credential

from streamsx.topology.topology import *
from streamsx.topology.schema import *
import streamsx.messagehub as messagehub
from pathlib import Path

import time
import datetime
import argparse


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
        self.datalen =  len(self.data)
        self.idx = 0

    def __exit__(self):
        """required if you have __enter__()"""
        pass

    def __next__(self):
        if (self.idx  >= self.datalen):
            ts = time.time()
            print("Resetting index @ ", datetime.datetime.fromtimestamp(ts).isoformat() )
            self.idx = 0
        chunk  = self.data[self.idx]
        self.idx += 1
        time.sleep(self.waitPeriod)
        return(chunk)



def jsonFileHub(jobName, nameSpace, mhTopic, jsonDataPath):
    topo = Topology(jobName, nameSpace)

    # Add the file to the sab so it will be in etc when deployed
    topo.add_file_dependency(jsonDataPath, "etc")
    jsonDataFile = os.path.basename(jsonDataPath)
    print(jsonDataFile)

    allEvents = topo.source(FileFeed(filename=jsonDataFile))
    reefer5dict = allEvents.filter(lambda t: t['id']=='Reefer_5', name="filterReefer_5")
    # convert to tuple + drop fields
    reefer5tuple = reefer5dict.map(lambda t: t, schema='tuple<float32 tempC, int32 amp>')
    # tuples plot in the console.
    reefer5tuple.view(buffer_time=2.0, sample_size=50, name="viewReefer5")

    # Send to message hub.
    allEvents = allEvents.as_string()
    messagehub.publish(allEvents, topic=mhTopic)
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
    parser.add_argument('--mhTopic', help="MessageHub topic to to send ekg events out on.", default="jsonEvents")
    parser.add_argument('--jsonData', help="Json data file, list of records to push ", default="reeferTrack.json")

    args = parser.parse_args()
    topo = jsonFileHub(jobName=args.jobName, nameSpace=args.nameSpace, mhTopic=args.mhTopic, jsonDataPath=args.jsonData)

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
          cancel=args.cancel, )
    print("Process status:%s" % submitStatus)



