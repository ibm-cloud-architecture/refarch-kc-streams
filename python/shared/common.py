from streamsx.topology import context
from streamsx.topology import context
import zipfile
import os
from streamsx.rest import *
import creds.credential as credential


"""
Create a service and create the Credentials, 
move them in here, needed to connect to the
service. 
"""

def build_streams_config(service_name, credentials):
    vcap_conf = {
        'streaming-analytics': [
            {
                'name': service_name,
                'credentials': credentials,
            }
        ]
    }
    trace_conf = {
        'tracing':'info',
    }

    config = {
        context.ConfigParams.VCAP_SERVICES: vcap_conf,
        context.ConfigParams.SERVICE_NAME: service_name,
        context.ConfigParams.FORCE_REMOTE_BUILD: True,
    }
    return config

def decryptCredentials(zipPath="shared/creds", cryptFile="credenital.py.zip", decryptFile="credential.py", pwd=None):
    """Decrypt the credential file that was encrypted with....
         > zip -e credential.py.zip credential.py
    """
    path = os.path.join(zipPath, decryptFile)
    if (os.path.isfile(path)):
        print("Credential file exists:" + path)
    else:
        print("Decryptying : " + path)
        if (pwd is None):
            raise Exception('Must define a password to decrypt file:' + file)
        with zipfile.ZipFile(os.path.join(zipPath, cryptFile)) as zip_ref:
            zip_ref.extract(decryptFile, path=zipPath, pwd=str.encode(pwd))


def cancel_job(service_name, streams_conf, namespace, name=None):
    """
    This will cancel jobs based upon namespace and name. If name is not
    provided all jobs in the namespace will be can canceled, this does not
    use the force flag at the moment.

    :param service_name:
    :param streams_conf:
    :param namespace:
    :param name:
    :return:
    """

    sc = StreamingAnalyticsConnection(service_name=service_name,
                                      vcap_services=streams_conf.get('topology.service.vcap'))

    if (name == None):
        checkName = namespace + "::"
    else:
        checkName = namespace + "::" + name
    instances = sc.get_instances()
    jobs_canceled = 0
    for instance in instances:
        jobs = instance.get_jobs()
        for job in jobs:
            print("Potential job to cancel:%s" % job.applicationName)
            if (job.applicationName.startswith(checkName)):
                print(" + Canceling job:%s application:%s" % (job.name, job.applicationName))
                print(" + Health before cancel : %s" % job.health)
                job.cancel()
                jobs_canceled += 1
    if (jobs_canceled == 0):
        print("*** No jobs canceled")

def submitProcess(topology=None, streamsService=None, serviceType=None, buildType=None, jobName=None, cancel=False ):
    #
    #   With the composed topology, process it. Build a bundle, submit to build server or (eventually)
    #   send to ICP.
    #   - streamsService : where appication will execute
    #   - serviceType : buildArchive | streams Application
    #   - send to build server then onto streams Service
    #

    print("Submission parameters:")
    print("  - serviceType:%s" % serviceType)
    print("  - buildType:%s" % buildType)
    print("  - jobName:%s" % jobName)
    print("  - cancel:%s" % cancel)
    streams_conf = build_streams_config(streamsService, credential.StreamsServices[streamsService])
    #
    if cancel:
        cancel_job(streamsService, streams_conf, name=jobName, namespace=jobName)
    # submit
    if (serviceType == "BUILD_ARCHIVE"):
        contextType = context.ContextTypes.BUILD_ARCHIVE
    else:
        contextType = context.ContextTypes.STREAMING_ANALYTICS_SERVICE
    submitStatus = context.submit(contextType, topology, config=streams_conf)
    return submitStatus




if __name__ == '__main__':
    streams_conf = build_streams_config("StreamingTurbine", credential.streamingTurbine)
    cancel_job("StreamingTurbine", streams_conf, "GdaxHub", "GdaxHub")

