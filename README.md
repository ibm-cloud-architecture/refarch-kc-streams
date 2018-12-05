# K Container Shipment Use Case: IBM Streaming Analytics Application

## Requirements

## Application Structure

### Application Inputs

### Application Outputs

## Development Environment

Application development can be done on any Linux system with the necessary packages installed.
Build is performed with a cloud based service and the application execution also occurs on a 
cloud based service.

### Prerequisites

The application has been written and validated with Python version 3.5, so that version is recommended
for using this application,

First, ensure that Python 3.5 is installed on your system:
```bash
TBD
```

To set up a Python 3.5 virtual environment, do the following:
```bash
virtualenv --python=python3.5 .venv
source .venv/bin/activate
python --version
```
### Packages   

Streams package that supports building streams.  Use a specific version due to errors 
hit with the most current level of streamsx. 
```bash
pip install streamsx
pip install --upgrade streamsx==1.11.3a0
```
Install the messagehub support
```bash
pip install streamsx.messagehub
```
Communication with REDIS to monitor real time.
```bash
pip install redis 
```
## Contents roots
 - python/shared/creds
 - python/shared
 - python/containerSimulator
 

## Package hints.
To check for the latest version of a package. 
```bash
# list all the modlules.
pip install streamsx==*
```

To upgrade to a specfic version of a package. 
```bash
pip3 install --upgrade streamsx==1.11.3a0
```

### Create Streams Instance

## Python
- SmokeTestEKG.py : SmokeTest for all the components. Sends EGK data at 1sec intervals. 
 
## Testing 
Run the following scripts to start the simulator for data creation and the application.
```bash
ReeferMonRun.sh
SimulatorRun.sh
```
Note: The SimulatorRun script will be depricated & removed.

### Ship location
- [short location ](https://www.navcen.uscg.gov/?pageName=AISMessagesA)
- [long location ](https://www.navcen.uscg.gov/?pageName=AISMessage27)


# IBM Streaming Analytics References 
 - [Developing IMG Streams Applications with Phython](http://ibmstreams.github.io/streamsx.documentation/docs/python/1.6/python-appapi-devguide/index.html)
-  [Streams Python tutorial](https://developer.ibm.com/courses/all/streaming-analytics-basics-python-developers/)  
 - [streamsx documentation](https://pypi.org/search/?q=streamsx)
 - [IBM Streams documentation](http://ibmstreams.github.io/streamsx.documentation/) 
 - [IBM Streams Python Support](https://streamsxtopology.readthedocs.io/en/latest/index.html)

