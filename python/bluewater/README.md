# Bluewater * Monitoring Bluewater 
Triton (/ˈtraɪtən/; Greek: Τρίτων Tritōn) is a mythological Greek god, the messenger of the sea. He is the son of Poseidon and Amphitrite, god and goddess of the sea respectively, and is herald for his father.


Processes tuples arriving via MessageHub

## MonitorRun.py
Submits the reefer jobs

### reeferMon.py
Recieves tuples and pushes them to Redis, the redis.ipynb notebook
will graph the values. 

### reeferRange.py 
Based upon threashold file values are filtered an averaged.   

## TestMonitory.py
Will drive the tests when I work out issues with the test harness. 



