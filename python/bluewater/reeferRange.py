# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2017
"""
Monitor shipboard container verify it's within bounds.

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
import numpy as np

import csv


class ExampleMap(object):
    def __init__(self, val_var):
        self.valvar = val_var
        pass
def __call__(self, dct):
    print("type:", type(dct))
    print("data:", dct)
    return dct


class AggTemp():
    def __init__(self, container_thresholds=None):
        self.thresholds = container_thresholds

    def __call__(self, dct):
        dct['avgC'] = None
        if dct['id'] in self.thresholds:
            contain = self.thresholds[dct['id']]
            contain['history'].append(dct['tempC'])
            dct['avgC'] = np.mean(contain['history'])
            print("history:", dct)
        return dct


class OutOfRangeTemp(object):
    def __init__(self, container_thresholds=None):
        """
        Return False if 'tempC' outside of container_thresholds 'lowC' and 'highC'
        :param container_thresholds:
        """
        self.thresholds = container_thresholds

    def __call__(self, dct):
        """
        :param self:
        :param dct:
        :return: True if out of range,
                 False if not in thresholds, avgC is None or in range
        """

        if dct['id'] not in self.thresholds:
            return False
        print("test id:", dct['id'])
        contain = self.thresholds[dct['id']]
        print("test contain:", contain)
        print("test against:", dct['avgC'])
        if dct['avgC'] is None:
            return False
        if contain['lowC'] <= dct['avgC'] <= contain['highC']:
            print("test false")
            return False
        return True


def container_ranges(csv_file=None):
    ranges = None
    if csv_file is None:
        ranges = dict({'Reefer_1': {'lowC': -20, 'highC': 2, 'history': collections.deque(maxlen=10)},
                   'Reefer_2': {'lowC': -20, 'highC': 1, 'history': collections.deque(maxlen=10)}
                   })
    return ranges


def monitor(job_name, name_space, mh_topic, redis_base=None):
    topo = Topology(job_name, name_space)
    topo.add_pip_package('streamsx.messagehub')

    ranges = container_ranges(None)
    fromMh = streamsx.messagehub.subscribe(topo, schema=CommonSchema.Json, topic=mh_topic)
    aggTemp = fromMh.map(AggTemp(container_thresholds=ranges), name="aggTemp")
    filterRange = aggTemp.filter(OutOfRangeTemp(container_thresholds=ranges), name="rangeFilter")

    filterRange.sink(TransmitRedis(credentials=credential.redisCredential,
                                   dest_key=redis_base + "/outOfRange", chunk_count=10), name="rangeRedis")
    aggTemp.sink(TransmitRedis(credentials=credential.redisCredential,
                               dest_key=redis_base + "/allRange", chunk_count=10), name="allRedis")

    return topo


