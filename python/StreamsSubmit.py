# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019
"""
Run the monitoring of reefers

*****
NOTES
*****

"""
import sys
print("current syspath", sys.path)
import common
import argparse
from pathlib import Path
import reeferMon
import reeferRange
import jsonPlayback


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reefer Monitor')
    parser.add_argument('--run', help="Streams application to build/run", choices=['mon', 'range', 'simulator'], required=True)
    parser.add_argument('--pwd', help="password to decrypyt credential file", default=None)
    parser.add_argument('--streamsService', help="Name of the Streams Analytics service", default="Streaming3Turbine")
    parser.add_argument('--serviceType', help="Type of service to build: STREAMING_ANALYTICS, BUILD_ARCHIVE.",
                        default="STREAMING_ANALYTICS")
    parser.add_argument('--buildType',
                        help="Either 'DISTRIBUTED' or 'BUNDLE' determines if scripts+submit or just scripts.",
                        default="DISTRIBUTED")
    defJobName = Path(parser.prog).resolve().stem
    parser.add_argument('--jobName', help="Name to assign to the job name", default=defJobName)
    parser.add_argument('--nameSpace', help="Name to assign to the namespace", default=defJobName)
    parser.add_argument("--cancel", help="Cancel active job before submitting job, uses jobName, nameSpace",
                        default=True)
    # application specfic arguments
    #parser.add_argument('--mhTopic', help="MessageHub topic to to send ekg events out on.", default="jsonEvents")
    parser.add_argument('--redisBase', help="Redis monitor path base path.", default="/score")

    parser.add_argument('--jsonData', help="Simulations data file", default="containerSimulator/reeferFire.json")
    parser.add_argument('--messageWait', help="Number of seconds to wait between messages", default=".02")

    args = parser.parse_args()
    print("Resolved args:", args)

    topology = None
    topics = {"ship": "magsShip", "container": "magsContainer", "problem": "magsProblem"}
    if args.run == "mon":
        topology = reeferMon.monitor(job_name=args.jobName, name_space=args.nameSpace,
                   redis_base=args.redisBase, topic=topics)
    if args.run == "range":
        topology = reeferRange.monitor(job_name=args.jobName, name_space=args.nameSpace,
                   mh_topic=args.mhTopic, redis_base=args.redisBase)
    if args.run =="simulator":
        topology = jsonPlayback.json2FileHub(jobName=args.jobName, nameSpace=args.nameSpace,
                       topic=topics,
                       jsonDataPath=args.jsonData,
                       message_wait=float(args.messageWait))

    try:
        import creds.credential as creds
    except ImportError:
        common.decryptCredentials(zipPath="../shared/creds/", cryptFile="credential.py.zip",
                                  decryptFile='credential.py', pwd=args.pwd)
        import creds.credential as creds
    submitStatus = common.submitProcess(topology=topology,
                                        streamsService=args.streamsService,
          buildType=args.buildType,
          serviceType=args.serviceType,
          jobName=args.jobName,
          cancel=args.cancel, )
    print("Process status:%s" % submitStatus)
