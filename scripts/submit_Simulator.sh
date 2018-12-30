#!/usr/bin/env bash
## Submit application from local system,
## depends on correct version of Java/Python installed
cd ../python
export PYTHONPATH=./shared:./shared/creds:./bluewater:./containerSimulator
python StreamsSubmit.py --run simulator --jobName magsSim --nameSpace magsSim
