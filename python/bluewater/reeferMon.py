# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2017
"""
Monitor shipboard reefers (refrigerated containers) traveling over blue water.

*****
NOTES
*****

- Pushing data to redis in order that something viewport into the processing.
- Sample record
   type: <class 'dict'>
   data: {'id': 'Reefer_5', 'ts': '2018-01-01 21:44:00',
       'oTemp': 22.1,
       'latitude': 10.11291508, 'longitude': 83.09646606,
       'amp': 55.730234304187434, 'tempC': 1.974183120145919}

"""

import common
import credential
import argparse
from streamsx.topology.schema import *
from streamsx.topology.topology import Topology
from streamsx.topology.schema import CommonSchema
import streamsx.messagehub
from pathlib import Path
from resourceAccess import TransmitRedis
from random import random




def augment_weather(iDict):
    # TODO use lat/long when
    """
    Put some weather data into the dictionary
    :param iDict:
    :return:
    """
    iDict['weatherC'] = (random() * 10) + 10
    return(iDict)

def format_fire(iDict):
    iDict['severity'] = "fire"
    iDict['issue'] = "combustion within container"
    iDict['status'] = "active"
    return(iDict)



class TagTuple(object):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, in_dict):
        in_dict['tag'] = self.tag
        print(in_dict)
        return in_dict


class Consolidate(object):
    """
    Consolidate interleaved messages : 'ship', 'container'

    'ship' messages data is stored in a dictionary, the data is not propated
    'container' uses 'shipId' to extract the stored message data.
    """

    def __init__(self):
        self.shipRegister = dict()
        pass

    def __call__(self, indict):
        print("consolidate", indict)
        if indict['tag'] == "ship":
            self.shipRegister[indict['shipId']] = {"longitude": indict["longitude"], "latitude": indict['latitude']}
            return None
        # we are processing a container
        enrich = self.shipRegister.get(indict['shipId'],{"latitude": 0.0, "longitude": 0.0})
        indict.update(enrich)
        return indict



def monitor(job_name, name_space, mh_topic, redis_base=None):
    topo = Topology(job_name, name_space)
    topo.add_pip_package('streamsx.messagehub')
    shipMh = streamsx.messagehub.subscribe(topo, schema=CommonSchema.Json, topic="bluewaterShip", name="shipMH")
    shipMh = shipMh.map(TagTuple("ship"), name="shipTag")
    containerMh = streamsx.messagehub.subscribe(topo, schema=CommonSchema.Json, topic="bluewaterContainer",
                                                name="containerMH")
    containerMh = containerMh.map(TagTuple("container"), name="containerTag")


    interLeaved = shipMh.union({containerMh})

    consolidated = interLeaved.map(Consolidate(), name="consolidate")

    complete = consolidated.map(augment_weather, name="weatherAugment")

    filterFire = complete.filter(lambda t: t['tempC'] > 200.0 , name="fireTest")
    formatFire = filterFire.map(format_fire, name="fireFormat")

    formatFire.sink(TransmitRedis(credentials=credential.redisCredential,
                                     dest_key=redis_base + "/bluewater/fire", chunk_count=100), name="fireRedis")

    messageFire = formatFire.as_json(name="fireJson")
    streamsx.messagehub.publish(messageFire, topic="bluewaterProblem", name="problemMH")

    return topo


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reefer Monitor')
    parser.add_argument('--pwd', help="password to decrypyt credential file", default=None)
    parser.add_argument('--streamsService', help="Name of the Streams Analytics service", default="Streaming3Turbine")
    parser.add_argument('--serviceType', help="Type of service to build: STREAMING_ANALYTICS, BUILD_ARCHIVE.",
                        default="STREAMING_ANALYTICS")
    parser.add_argument('--buildType',
                        help="Either 'DISTRIBUTED' or 'BUNDLE' determines if scripts+submit or just scripts.",
                        default="DISTRIBUTED")
    defJobName = Path(parser.prog).resolve().stem
    parser.add_argument('--jobName', help="Name to assign to the job name", default=defJobName)
    parser.add_argument('--nameSpace', help="Name to assign to the namespace", default=defJobName)
    parser.add_argument('--cancel', help="Cancel active job before submitting job, uses jobName, nameSpace",
                        default=True)
    # application specfic arguments...
    parser.add_argument('--mhTopic', help="MessageHub topic to to send ekg events out on.", default="jsonEvents")
    parser.add_argument('--redisBase', help="Redis monitor path base path.", default="/score")

    args = parser.parse_args()

    topology = monitor(job_name=args.jobName, name_space=args.nameSpace,
                   mh_topic=args.mhTopic, redis_base=args.redisBase)

    try:
        import creds.credential as creds
    except ImportError:
        common.decryptCredentials(zipPath="../shared/creds/", cryptFile="credential.py.zip",
                                  decryptFile='credential.py', pwd=args.pwd)
        import creds.credential as creds
    submitStatus = common.submitProcess(topology=topology,
                                        streamsService=args.streamsService,
          buildType=args.buildType,
          serviceType=args.serviceType,
          jobName=args.jobName,
          cancel=args.cancel, )
    print("Process status:%s" % submitStatus)
