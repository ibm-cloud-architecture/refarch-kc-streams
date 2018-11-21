# coding=utf8
"""
containerSimulation.py : Generate a number of refrigerated containers (Reefer Units) transorted
on ship. The reefers has a operating range, values that effect this units are the outside temp,
number of amps used in a cooling phase.

Outside temp. is  influenced by:
     weather :  implemented
     container location : todo - close to the equator, higher the temp.
     time of day : todo : closer to noon, higher the temp.


Output :
  file :
  stream / message hub : todo

@author: Stefan Scherfke
@contact: stefan.scherfke at uni-oldenburg.de
@adapted : mags
"""

from math import exp

import logging
import random
import csv
import json
from datetime import datetime, timedelta
import argparse
import simpy

log = logging.getLogger('reefer')


class Reefer(object):
    """
    This class represents a simulated fridge.
    It's temperature T for and equidistant series of time steps is computed by
    $T_{i+1} = \epsilon \cdot T_i + (1 - \epsilon) \cdot \left(T^O - \eta
    \cdot \frac{q_i}{A}\right)$ with $\epsilon = e^{-\frac{\tau A}{m_c}}$.

    Added elements:
    - fetchLoc : function that returns the current lat,lng based upon id passed in
    - locationTemp :
    - id : String to identify the reefer.
    """

    def __init__(self, env, id="R1", fetchLoc=None, reeferLog=None, locationTemp=None,  T_O=20.0, A=3.21, m_c=15.97, tau=1.0 ,
                 eta=3.0, q_i=0.0, q_max=70.0,
                 T_i=5.0, T_range=[5.0, 8.0], noise=False):
        """
        Init all required variables.

        @param sim:       The SimPy simulation this process belongs to
        @type sim:        SimPy.Simulation
        @parm id:         Reefer id
        @func fetchLoc    Fetch the current location based upon step
        @func locationTemp Return the outside temp based upon the current location.
        @param T_O:       Outside temperature
        @param A:         Insulation
        @param m_c:       Thermal mass/thermal storage capacity
        @param tau:       Time span between t_i and t_{i+1}
        @param eta:       Efficiency of the cooling device
        @param q_i:       Initial/current electrical power
        @param q_max:     Power required during cool-down
        @param T_i:       Initial/current temperature
        @param T_range:   Allowed range for T_i
        @param noise:     Add noise to the fridge's parameters, if True
        @type noise:      bool
        """
        self.env = env
        self.id = id
        self.fetchLoc = fetchLoc
        self.reeferLog = reeferLog
        self.locationTemp = locationTemp
        self.T_O = T_O
        self.A = A
        self.m_c = random.normalvariate(20, 4.5) if noise else m_c
        self.tau = tau
        self.eta = eta
        self.q_i = q_i
        self.q_max = q_max
        self.T_i = random.uniform(T_range[0], T_range[1]) if noise else T_i
        self.T_range = T_range
        self.action = env.process(self.run)

    @property
    def run(self):
        """
        Calculate the fridge's temperature for the current time step.
        """
        while True:
            locTs = self.fetchLoc(self.env.now)
            self.T_O = self.locationTemp(locTs)

            epsilon = exp(-(self.tau * self.A) / self.m_c)
            self.T_i = epsilon * self.T_i + (1 - epsilon) \
                       * (self.T_O - self.eta * (self.q_i / self.A))
            last_qi = self.q_i
            if self.T_i >= self.T_range[1]:
                self.q_i = self.q_max  # Cool down
                self.q_i = random.uniform(self.q_max * 0.60, self.q_max )
            elif self.T_i <= self.T_range[0]:
                self.q_i = 0.0  # Stop cooling

            logEntry = {'id': self.id, 'tempC': self.T_i, 'amp': last_qi, 'latitude': locTs['latitude'], 'longitude':locTs['longitude'], 'ts':locTs['ts'], 'oTemp':self.T_O}
            self.reeferLog(logEntry)
            log.debug('{"id":"%s","Temp°C":%2.2f,"amp":%2.2f "loc":%s oTemp:%d},'% (self.id, self.T_i, last_qi, locTs, self.T_O))

            yield self.env.timeout(self.tau)

    def coolDown(self):
        """
        This is a over ride function.
        """
        self.q_i = self.q_max



class ReeferLog(object):
    def __init__(self):
        self.reeferLog = list()

    def __call__(self, dict):
        self.reeferLog.append(dict)

    def fetch(self):
        """
        fetch the log
        :return:
        """
        return self.reeferLog


class LocationTemp():
    """
    Hourly temp file, each line number within the file is the hours temp.

    If line 49 is -20 then the outside temp is will be -20 on
    the 2 days and 1 hour after the start of the vouage.

    File is expected to be csv, with two columns date and tempC
    a header
    """
    def __init__(self, hourlyTempFile="../data/weatherJanNY.csv",
                 startTime="2018-1-1 00:00:00"):
        with open(hourlyTempFile) as csvfile:
            data = csv.reader(csvfile, delimiter="|")
            next(data, None)     # skip header
            hourTemps = [row[1] for row in data]
        self.hourTemps = hourTemps
        self.startHour = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")

    def __call__(self, dict):
        endHour = datetime.strptime(dict['ts'], "%Y-%m-%d %H:%M:%S")
        diff = endHour - self.startHour
        days, seconds = diff.days, diff.seconds
        hour  = days*24 + seconds //3600
        return(float(self.hourTemps[hour]))


class ShipTrack(object):
    def __init__(self, csvFile, sampleIncrement=120, startTime="2018-01-01 00:00:00"):
        """
        :param csvFile: file with gps data
        :param sampleIncrement: number of seconds between element
        :param startTime: when clock is to start
        """
        self.gpsTrack = list()
        self.startTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")

        self.secs = sampleIncrement
        with open(csvFile) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.gpsTrack.append({'longitude':float(row['Longitude']),'latitude':float(row['Latitude'])})

    def length(self):
        return(len(self.gpsTrack))

    def __call__(self, idx):
        secs = self.secs * idx
        gpsTime = self.startTime + timedelta(seconds=secs)
        stage = self.gpsTrack[int(idx)]
        stage['ts'] = gpsTime.__str__()
        return stage


if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Generate gps track for reefer containers')
    parser.add_argument('--gpsFile', help="csv file with headers:Longitude,Latitude,Altitude", default="../data/latlondata.csv")
    parser.add_argument('--tempuratureHourly', help="hourly temp with header:date, tempC", default="../data/weatherJunNY.csv")
    parser.add_argument('--outFile', help="output of gps track json file ", default="reeferTrack.json")
    parser.add_argument('--reefers', help="number of reefers to generate", default="10")
    parser.add_argument('--startTime', help="start time", default=datetime(2018, 1, 1, hour=0, minute=0, second=0, microsecond=0)
)


    args = parser.parse_args()


    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')

    shipTrack = ShipTrack(args.gpsFile)
    trackLength  = shipTrack.length() - 20

    reeferLog = ReeferLog()
    locationTemp = LocationTemp(args.tempuratureHourly)
    reefer = list()
    tau = 1. / 60  # Step size 1min
    aggSteps = 15  # Aggregate consumption in 15min blocks
    params = {'tau': tau}

    sim = simpy.Environment()

    for idx in range(int(args.reefers)):
        reeferId = "Reefer_%d" % idx
        reefer.append(Reefer(sim, id=reeferId, fetchLoc=shipTrack, reeferLog=reeferLog, locationTemp=locationTemp))
    sim.run(until=trackLength)
    ## write out results state in shipTrack
    with open(args.outFile, 'w') as outfile:
        json.dump(reeferLog.fetch(), outfile, indent=2)


