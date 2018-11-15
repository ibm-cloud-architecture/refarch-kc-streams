# Streams Application using 

## Prerequisite : 
Python3 prefer Anaconda 

## Packages   

Streams package that supports building stream 
```bash
pip install streams 
```
Install the messagehub support
```bash
pip install streams.messagehub

```
Communcation with REDIS to monitor realtime.
```bash
pip install redis 
```

## Package hints.
To check for the latest version of a package. 
```bash
# list all the modlules.
pip install streamx==*
```

To upgrade to a specfic version of a package. 
```bash
pip3 install --upgrade streamsx==1.11.3a0
```


## Requirement


### Create Streams Instance

## Python
- SmokeTestEKG.py : SmokeTest for all the components. Sends EGK data at 1sec intervals. 
 
## Testing 

## Simulation 
Format of the data.
### Ship Data
- loc (lat,lng)
- ts 
- ship# 

### Reefer data : 
- temp (F)
- loc (lat,lng)
- power 
- ts 
- unit #

### Ship location
- [short location ](https://www.navcen.uscg.gov/?pageName=AISMessagesA)
- [long location ](https://www.navcen.uscg.gov/?pageName=AISMessage27)


### 