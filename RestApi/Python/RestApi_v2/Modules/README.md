## The BreakingPoint RESTv2 API Python Wrapper 
[![pypi](https://img.shields.io/pypi/v/bps-restpy.svg)](https://pypi.org/project/bps-restpy)
[![python](https://img.shields.io/pypi/pyversions/bps-restpy.svg)](https://pypi.python.org/pypi/bps-restpy)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![downloads](https://pepy.tech/badge/bps-restpy)](https://pepy.tech/project/bps-restpy)

## BreakingPoint detail
Network testing with  [BreakingPoint®](https://www.ixiacom.com/products/network-security-testing-breakingpoint). By simulating real-world legitimate traffic, distributed denial of service (DDoS), exploits, malware, and fuzzing, BreakingPoint validates an organization’s security infrastructure, reduces the risk of network degradation by almost 80%, and increases attack readiness by nearly 70%. And with our new TrafficREWIND solution, you'll get even more realistic and high-fidelity validation by adding production network insight into BreakingPoint test traffic configuration
More details:

## Install the package
```
pip install --upgrade bps-restpy
```

## Start scripting
```python
"""This script demonstrates how to get started with bps_restpy scripting.

# Title:  Python Script Sample To Run a Canned Test.
# Actions:
#   1. Login to BPS box
#   2. Reserve ports
#   3. Load a test from the box and start the run
#   4. Wait for the test to finish
#   5. Get test result
#   6. Get and print the Synopsis page from report
#   7. Unreserve ports
#   8. Logout


#================

########################################
import time, sys, os
# Import corresponding BPS RESTv2 python2.7/ 3 library from outside the folder with samples.
sys.path.insert(1, os.path.dirname(os.getcwd()))

from bps_restpy.bps import BPS, pp

########################################


########################################
# Demo script global variables
########################################
# Demo script global variables
canned_test_name = 'AppSim'
#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'


slot_number = 2
port_list   = [0, 1]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


########################################
print("Load a canned test: ")
bps.testmodel.load(canned_test_name)

########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=canned_test_name, group=2)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
print("Test Run Id: %s"%run_id)

#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
while run_id in runningTests_Ids:
     run_state =  bps.topology.runningTest[run_id].get()
     #print progress if test started
     try: print ('progress: %s%% , runtime %ss' % (run_state['progress'], run_state['runtime'] ))
     except: print ("Starting...")
     time.sleep(2)
     #update the current running tests
     runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 

print("~The test finished the execution.")
results = bps.reports.search(searchString=canned_test_name, limit=10, sort="endTime", sortorder="descending")
result  = results[0]
print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)

print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()
```
wew
## Documentation
Documentation is available using the following methods:
* [Online web based documentation and samples](https://github.com/OpenIxia/BreakingPoint)
* On your BreakingPoint System RestApi found near the BreakingPoint App  
* Documentation available in the online doc browser is also inlined in each class, property and method and can be viewed using the python help command
  ```python
  from bps_restpy.bps import BPS, pp
  
  #login to your Breaking Point System
  help(BPS)
  bps = BPS('your_bps_IP_or_FQDN', 'admin', 'admin')
  
  help(bps.testmodel.importModel)
  
  ```

## Additional Samples
Visit the [OpenIxia breakingpoint-restpy sample site maintained by solution architects](https://github.com/OpenIxia/BreakingPoint) for in depth end-to-end samples that demonstrate the following:
* building a configuration
  * from scratch
  * from an existing BreakingPoint configuration
* running the configuration
  * connecting ports to hardware
  * starting protocols
  * starting traffic
* getting statistics
  * port stats
  * traffic stats


