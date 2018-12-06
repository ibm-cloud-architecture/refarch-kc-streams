# K Container Shipment Use Case: IBM Streaming Analytics Application

This streaming application demonstrates real time event processing applied to inputs from
the ships and containers used in the K Container Shipment Use Case.  It is designed to monitor
refrigerated containers, known as reefers, stowed on ships which are traveling over blue water.

## Table Of Contents

* [Application](#application)
* [Development Environment](#development-environment)
* [References](#references)
* [IBM Cloud Streaming Analytics Instance](#ibm-cloud-streaming-analytics-instance)
* [Build and Execute the Application](#build-and-execute-the-application)

## Application

### User Stories 

- [ ] As a Shipping Agent, I’d like to efficiently understand the health of and manage the operations of reefer containers in transit, to ensure that I am effectively protecting goods in my care, and managing cost.
- [ ] As a Shipping Agent, I need to understand when  a container isn’t operating within normal boundaries and automatically take corrective action.
- [ ] As a Shipping Agent, I’d like to understand when a container temperatures are trending towards a boundary and may need a reset.
- [ ] As a Shipping Agent, I’d like to understand when containers may have a potential failure so I can proactively take action to protect goods in transit.
- [ ] As a Shipping Agent, I’d like to understand when a container is failing so I can take corrective action.
- [ ] As a Shipping Agent, I’d like to automatically manage container settings based on any course or route deviations or rerouting events.

### Application Structure

![](streams-app.png)

### Application Logic

1. Temp is rising && no power consumption  ==> reset power and thermostat
2. Temp is rising && power consumption is flat ==> Potential Failure -> reset and notify
3. Temp is rising and power is rising ==> Failing and notify
4. Temp is dropping below bounds ==> reset thermostat

## Development Environment

Application development can be done on any Linux system with the necessary packages installed.
Build is performed with a cloud based service and the application execution also occurs on a 
cloud based service.  Because this application leverages cloud services, there is no need to
install IBM Streams on your development system.

### Prerequisites

The application has been written and validated with Python version 3.5, so that version is recommended
for running this application,

First, ensure that Python 3.5 is installed on your system:
```bash
python3.5 --version
```
If it is not installed, follow the process described by your OS vendor.  As an example, for CentOS:
```bash
sudo yum install python35u
```

Next you will need to set up a Python 3.5 virtual environment, as follows: 
```bash
virtualenv --python=python3.5 .venv
source .venv/bin/activate
python --version
```
Some open source packages for IBM Streams are required for this application.  
In some cases, specific versions have been selected for compatibility reasons.
To install these packages, run the follow commands from your python virtual environment.

```bash
pip install streamsx
pip install --upgrade streamsx==1.11.3a0
pip install streamsx.messagehub
pip install redis 
```
### Code Modules Summary
 - python/shared/creds
 - python/shared
 - python/containerSimulator
 

## IBM Cloud Streaming Analytics Instance

### Create the Environment

### Manage the Environment

## Build and Execute the Application

The following script performs the application build and submits it to the IBM Cloud Streaming Analytics service.  Once it has been successfully run, the application will be running on the cloud watching for input events and producing output events in response on the Event Streams buses.

```bash
ReeferMonRun.sh
```

### Items that will be depricated and removed.

- SmokeTestEKG.py : SmokeTest for all the components. Sends EGK data at 1sec intervals. 
 
Run the following script to start the simulator:
```bash
SimulatorRun.sh
```

# References 
 - [Developing IMG Streams Applications with Phython](http://ibmstreams.github.io/streamsx.documentation/docs/python/1.6/python-appapi-devguide/index.html)
-  [Streams Python tutorial](https://developer.ibm.com/courses/all/streaming-analytics-basics-python-developers/)  
 - [streamsx documentation](https://pypi.org/search/?q=streamsx)
 - [IBM Streams documentation](http://ibmstreams.github.io/streamsx.documentation/) 
 - [IBM Streams Python Support](https://streamsxtopology.readthedocs.io/en/latest/index.html)
 - [ship short location ](https://www.navcen.uscg.gov/?pageName=AISMessagesA)
 - [ship long location ](https://www.navcen.uscg.gov/?pageName=AISMessage27)

