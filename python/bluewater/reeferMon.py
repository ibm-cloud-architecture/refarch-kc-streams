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

import credential
from streamsx.topology.schema import *
from streamsx.topology.topology import Topology
from streamsx.topology.schema import CommonSchema
import streamsx.messagehub
from resourceAccess import TransmitRedis
from random import random



class TagTuple(object):
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, in_dict):
        in_dict['tag'] = self.tag
        return in_dict

def augment_weather(iDict):
    # TODO lat/long in place
    """
    Put some weather data into the dictionary
    :param iDict:
    :return:
    """
    iDict['weatherC'] = (random() * 10) + 10
    return(iDict)

def format_heatwave(idict):
    idict['severity'] = "situational"
    idict['issue'] = "heatwave"
    idict['status'] = "top units get hotter"
    return idict


def format_unitDown(idict):
    idict['severity'] = "down"
    idict['issue'] = "unit is no longer functioning "
    idict['status'] = "temp exceeded and 0 amps"
    return idict


def format_fire(idict):
    idict['severity'] = "fire"
    idict['issue'] = "combustion within container"
    idict['status'] = "active"
    return idict


class Consolidate(object):
    """
    Consolidate interleaved messages : 'ship', 'container'

    'ship' messages {lat,long} is stored in a dictionary, the tuple is not propagated
    'container' uses 'shipId' to extract the stored message {lat, long}
    """

    def __init__(self):
        self.shipRegister = dict()
        pass

    def __call__(self, idict):
        if idict['tag'] == "ship":
            self.shipRegister[idict['shipId']] = {"longitude": idict["longitude"], "latitude": idict['latitude']}
            return None
        # we are processing a container
        enrich = self.shipRegister.get(idict['shipId'], {"latitude": 0.0, "longitude": 0.0})
        idict.update(enrich)
        return idict


""" Sample Recod
{'shipId': 'medusa', 'ts': '2018-01-01 00:06:00', 'amp': 0.0, 'weatherC': 12.808168421380408, 'tempC': -3.8947368077106654, 'latitude': 10.76488498, 'tag': 'container', 'containerId': 'Reefer_2', 'longitude': 78.71498106}
"""


class UnitDown():
    def __init__(self, temp_high=30, amp_low=0):
        self.fleet = dict()
        self.tempHigh = temp_high
        self.tempInit = temp_high - 2
        self.ampLow = amp_low
        self.ampInit = amp_low + 2
        pass

    def __call__(self, idict):
        fault = False
        t, a = idict['tempC'], idict['amp']
        # extract ship from fleet, extract container from ship
        ship = self.fleet.get(idict['shipId'], dict())
        cont = ship.get(idict['containerId'], {'tempC': self.tempInit,'amp': self.ampInit })

        if t > self.tempHigh and a <= self.ampLow and cont['tempC'] >self.tempHigh and cont['amp'] <= self.ampLow :
            fault = True
        # update for container, update the container of the ship , update the ship of the fleet
        cont.update({'amp':a, 'tempC':t})
        ship.update({idict['containerId']: cont})
        self.fleet.update({idict['shipId']: ship})
        return fault

class Heatwave():
    def __init__(self, ):
        pass

    def __call__(self, idict):
        #return idict
        return False



def monitor(job_name, name_space, redis_base=None, topic={'ship':'bluewaterShip', 'container':'bluewaterContainer', 'problem':'bluewaterProblem'}):
    topology = Topology(job_name, name_space)
    topology.add_pip_package('streamsx.messagehub')
    # fetch and tag tuples
    shipMh = streamsx.messagehub.subscribe(topology, schema=CommonSchema.Json, topic=topic['ship'], name="shipMH")
    shipMh = shipMh.map(TagTuple("ship"), name="shipTag")
    containerMh = streamsx.messagehub.subscribe(topology, schema=CommonSchema.Json, topic=topic['container'],
                                                name="containerMH")
    containerMh = containerMh.map(TagTuple("container"), name="containerTag")
    # normalize the tuples
    interLeaved = shipMh.union({containerMh})
    consolidated = interLeaved.map(Consolidate(), name="consolidate")
    complete = consolidated.map(augment_weather, name="weatherAugment")

    complete.print(tag="complete")
    # process the data
    heatwaveFiltered = complete.filter(Heatwave(), name="heatwaveTest")
    formatHeatwave = heatwaveFiltered.map(format_heatwave, name="heatwaveFmt")
    unitDownFiltered = complete.filter(UnitDown(), name="downTest")
    formatDown = unitDownFiltered.map(format_unitDown, name="downFmt")
    fireFiltered = complete.filter(lambda t: t['tempC'] > 200.0 , name="fireTest")
    formatFire = fireFiltered.map(format_fire, name="fireFmt")

    # colsolidate notification - redis + messagehub
    formatted = formatFire.union({formatDown, formatHeatwave})
    formatted.sink(TransmitRedis(credentials=credential.redisCredential,
                                     dest_key=redis_base + "/bluewater/notify", chunk_count=100), name="notifyRedis")
    messageProblem = formatted.as_json(name="castJson")
    streamsx.messagehub.publish(messageProblem, topic=topic['problem'], name="problemMH")

    return topology
