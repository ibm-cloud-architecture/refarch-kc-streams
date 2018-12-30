# Notes

# Docker Submit 
Docker image submits Monitor Streams process in the cloud.

To build
```bash
docker build -t cloudstreams -f Dockerfile-monitor . 
```

To Submit
```bash
docker run -t cloudstreams 
```

To debug
```bash
docker run -it cloudstreams bash 
``` 

## StreamsSubmit : submits to streams instance. 
Option --run  
- mon : bluewater/reeferMon
- simulator :  

