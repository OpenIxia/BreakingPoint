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
import time, sys, os, traceback
# Add bps_restpy libpath *required if the library is not installed
sys.path.append(os.path.join(os.path.dirname(__file__), r"../lib"))

from restPyWrapper3 import *

########################################


########################################
# Demo script global variables
########################################
# Demo script global variables
canned_test_name = 'AppSim'
#bps system info
bps_system  = '10.36.83.70'
bpsuser     = 'admin'
bpspass     = 'admin'
testGroup = 1

slot_number = 1
port_list   = [1.0, 2.0]
l47_resource = [0 , 1]
########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
retry_count = 0
bps.login()

########################################
print("Load a canned test: ")
bps.testmodel.load(canned_test_name)
########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': testGroup}])
print("Reserve L47 resources...")
for r in l47_resource:
    bps.topology.reserveResource(group = testGroup, resourceId = r, resourceType = "l47")


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=canned_test_name, group=testGroup)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
print("Test Run Id: %s"%run_id)
#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
retry_count = 0
try: 
    while True and retry_count <= 3:
        try:
            run_state = bps.topology.runningTest[run_id].get()
            stat_val = bps.testmodel.realTimeStats(int(testid), "ethRxFrameDataRate", -1)
        except Exception as err:
            if retry_count == 3:
                bps.logout()
                raise Exception("Exceeded the Retry limitation!")
            if type(err) == dict and "status_code" in err.keys() and err["status_code"] in [500, 503]:
                print("Retry the stats retrieiving in 5 seconds...")
                time.sleep(5)
                retry_count += 1
                continue
            else:
                bps.logout()
                raise Exception(err)
        try:
            state = run_state['completed']
        except KeyError:  # The key does not exist in a completed test-> should be treated as completed.
            print("Payload is not collected. The test is finished while collecting or the API is not providing the correct result.")
            traceback.print_exc()
            state = True
        if state:
            break
        else:
            print("Time Elapsed: " + str(run_state['runtime']) + "(%s%%)" % str(run_state['progress']) )
            if run_state['progress'] is None:
                time.sleep(1)
            continue
    print("Test completed")
            # for k in self.csv_dumper_objects.keys():
            #     self.csv_dumper_objects[k].close_writer()
            # get_test_end_status()
except Exception as err:
    bps.logout()
    raise Exception(str(err)) 
print("~The test finished the execution.")
time.sleep(2)
print("Releasing resources...")
for r in l47_resource:
    bps.topology.releaseResource(group = testGroup, resourceId = r, resourceType = "l47")
print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': testGroup}])
bps.logout()
