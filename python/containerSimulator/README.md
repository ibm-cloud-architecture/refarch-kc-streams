# Conatainers on Ship Simulator : Shipping Containers crossing Bluewater 

Using simpy to generate a set of reefer containers moving over bluewater. The reefers temp is generated 
independently usng

**TODO** : generate events into Streams

## Moldules 
 - simpy
 
## Learning
 - [video](https://www.youtube.com/watch?v=Bk91DoAEcjY) SimPy introduction
 - [basic](https://simpy.readthedocs.io/en/latest/contents.html) : note the realtime simulations
 - [refrigerator](https://pythonhosted.org/SimPy/Manuals/Interfacing/ParallelSimPy/SimPyPP.html) : simulator derived from here
 
 
 ### Files
 - containersFile.py : generate container tracks into json file.
 - latlondata.csv : track data India - India to Sigapore 
  
  
### Sample data from run of containersFile.csv
```text
{
    "tempC": 2.16743565494168,
    "id": "Reefer_0",
    "ts": "2018-01-03 11:52:00",
    "latitude": 6.534462003,
    "longitude": 91.93153381,
    "amp": 55.467900564943385
  },
  {
    "tempC": 2.5343135699964074,
    "id": "Reefer_1",
    "ts": "2018-01-03 11:52:00",
    "latitude": 6.534462003,
    "longitude": 91.93153381,
    "amp": 52.10202347975249
  },
  {
    "tempC": 10.164932490533113,
    "id": "Reefer_2",
    "ts": "2018-01-03 11:52:00",
    "latitude": 6.534462003,
    "longitude": 91.93153381,
    "amp": 0.0
  },
```