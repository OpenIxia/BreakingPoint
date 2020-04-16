# Title:  Python Script made to create a Test Model from scrach.
# Actions:
#   1. Login to BPS box
#   2. Create a new test
#   3. Add components (AppSim + RR)
#   4. Save test
#   5. Clone components then disable the RR components.
#   6. Reserve ports
#   7. Run test and wait a few seconds
#   8. Get stats
#   9. Delete test from database and try to search it again
#  10. Unreserve ports and logout.




import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp



########################################
# Demo script global variables
appsim_component_name = "tempAppsim"
rr_component_name     = "tempRR"
test_name             = "Test_Model"

#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

slot_number = 1
port_list   = [0, 1]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


########################################
print "Create a new test: "
bps.testmodel.new()

print "Add components to the test."
bps.testmodel.add(name=appsim_component_name, type="appsim", active=True, component="appsim")

comp_Name = bps.testmodel.component["appsim_1"].label.get()
print "Component Name is: %s" % comp_Name

bps.testmodel.add(name=rr_component_name, type="routingrobot", active=True, component="routingrobot")
comp_Name = bps.testmodel.component["routingrobot_1"].label.get()
print "Component Name is: %s" % comp_Name

bps.testmodel.save(name=test_name, force=True)
test = bps.testmodel.search(searchString=test_name, limit=2, sort="name", sortorder="ascending")
print "Search result after save: "
print test

print "Clone the components: "
bps.testmodel.clone('routingrobot_1', 'routingrobot', True)
bps.testmodel.clone("appsim_1", 'appsim', True)

print "Change name for the cloned componets:"
bps.testmodel.component["appsim_2"].set({"label":"App2"})
bps.testmodel.component["routingrobot_2"].set({"label":"RR2"})

print "Components Status: "
pp(bps.testmodel.component.get())

print "Disable the RR components: "
bps.testmodel.component["routingrobot_1"].active.set(False)
bps.testmodel.component["routingrobot_2"].active.set(False)

########################################
print "Save test:"
bps.testmodel.save()

########################################
print "Reserve Ports"
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 1}])


########################################
print "Run test and Get Stats:"
test_id_json = bps.testmodel.run(modelname=test_name, group=1)
run_id = test_id_json["runid"]
print "Test Run Id: %s"%run_id

print "~Wait for test to begin initialization."
runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
while (runningTests["initProgress"] == None):
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    print "..."
    time.sleep(1)

print "~Wait for the initialization process "
init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
while( int(init_progress) <= 100 and runningTests["progress"] == None):
    init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    time.sleep(1)
    print "Initialization progress:   %s%s" % (init_progress, '%')

print "~Test is running. Get stats at every 2 seconds."
progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
while(type(progress) == str and int(progress) <= 100):
    pp(bps.testmodel.realTimeStats(int(run_id), "summary", -1))
    progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
    time.sleep(2)


########################################
print "Delete Test"
bps.testmodel.delete(name=test_name)
test = bps.testmodel.search(searchString=test_name, limit=2, sort="name", sortorder="ascending")
print "Search result after delete"
print test

########################################
print "Unreserve ports"
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p}])

z########################################
print "Session logout"
bps.logout()



