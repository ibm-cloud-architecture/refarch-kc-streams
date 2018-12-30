# Bluewater * Monitoring Bluewater 
Triton (/ˈtraɪtən/; Greek: Τρίτων Tritōn) is a mythological Greek god, the messenger of the sea. He is the son of Poseidon and Amphitrite, god and goddess of the sea respectively, and is herald for his father.


Processes tuples arriving via MessageHub


### reeferMon.py
Submit a job to the build server if it finishes successfully the job is submitted to Streaming Analatics Streaming3Turbine. 
Messages come in bluewaterShip & bluewaterContainer - when a notification needs to happen it goes out bluewaterProblem.

Use scripts/submitMonitor.sh to run from the command line. 
 
### reeferRange.py 
Based upon threshold file values are filtered an averaged.   

## TestMonitory.py
Will drive the tests when I work out issues with the test harness. 

## Messages

### topic: bluewaterShip
```json
{
    "latitude": 5.096282982,
    "longitude": 95.16426085
    "shipId": "medusa",
    "ts": "2018-01-04 01:54:00",
},
```

### topic: bluewaterContainer
```json
{
    "shipId": "medusa",
    "containerId": "Reefer_7",
    "tempC": : 12.2,
    "amp": 2,
    "ts": "2018-01-04 01:54:00"
}
```
### topic:bluewaterProblem
```json
{
    "shipId": "medusa",
    "containerId": "Reefer_7",
    "amp": 2,
    "tempC": 12.2,    
    "ts": "2018-01-04 01:54:12",
    "weatherC":12.0,
    "severity":"fire",
    "issue":"combustion tempurature exceeded",
    "status":"destroyed"
}
```


