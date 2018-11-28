#!/usr/bin/env bash
export PYTHONPATH=../shared:../shared/creds
python jsonPlayback.py --jsonData reeferFire.json --mhTopic testEvents --jobName testEvents --messageWait 0.02



