#!/usr/bin/env bash
## Submit application from local system,
## depends on correct version of Java/Python installed
cd ../python/bluewater
export PYTHONPATH=../shared:../shared/creds
python MonitorRun.py --run mon
