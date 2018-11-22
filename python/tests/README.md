# Unit test notes....

Tests using unittest. 

Recall that the code compiles on a server and is then submitted. A number of
faciliities are available to simplfy this. Some links:
- [module-streamsx.topology.tester](https://streamsxtopology.readthedocs.io/en/latest/streamsx.topology.tester.html#module-streamsx.topology.tester)
- [sample code](https://github.com/IBMStreams/streamsx.testing/tree/develop/examples/operators)


## Hints 

### Need to have VCAP_SERVICES set....  

```bash 
export VCAP_SERVICES=...shared/creds/vcap.json
```

### Invoke all tests in directory using..
```bash
python -m unittest
```
Or use the IDE...

This is what the vcap.json looks like (obvicated some portions)

The vcaap.json looks like...
```json
{
  "streaming-analytics": [
    {
      "name": "Streaming3Turbine",
      "credentials": {
        "apikey": "SZtizGEk0t0gIZb0xmO",
        "iam_apikey_description": "Auto generated apikey during resource-key operation for Instance - crn:v1:bluemix:public:streaming-analytics:us-south:a/309e3606a35c9fea12981876cd991b07:b11e1ab0-9570-44d0-950c-7b84b5abb817::",
        "iam_apikey_name": "auto-generated-apikeydd75",
        "iam_role_crn": "crn:v1:bluemix:public:iam::::ser:Manager",
        "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/309e32981876cd991b07::serviceid:ServiceId-761f23f0-ec9f-4eba-9f97-7cee5b99d19f",
        "v2_rest_url": "https://streams-app-service.ng.bluemix.net/v2/streaming_analytics/b11eb817"
      }
    }
  ]
}

```



The code is using the Streaming3Turbine service, credentials are defined here.
This is not the real vcap need to get your own. 

The vcap.json and the credential.py same data, get rid of the credenital - use the
standard which is vcap.json now. 
