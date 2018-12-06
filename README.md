# K Container Shipment Use Case: IBM Streaming Analytics Application

## Requirements

## Application Structure

![](streams-app.png)

### Application Inputs

### Application Outputs

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

