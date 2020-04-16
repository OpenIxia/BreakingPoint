# Title:  Python Script made to create a Test Model from scratch.
# Actions:
#   1. Login to BPS box
#   2. Load Canned test
#   3. Clone component (AppSim)
#   4. Save test
#   5. Reserve ports
#   6. Run test and monitor progress
#   7. Stop the test
#   8. Get values from report and display them in python
#   9. Export capture
#  10. Unreserve ports and logout.


#================

import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
# Demo script global variables
new_testmodel_name  = 's05_testModel'
#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

slot_number = 5
port_list   = [0, 4]

########################################

# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


########################################
print("Load a canned test: ")
bps.testmodel.load('AppSim')
#getting the last compponent from the test
component = bps.testmodel.component.get()[-1]
#cloning the abve component
bps.testmodel.clone(template = component['id'], type = component['type'], active = True)
clone = bps.testmodel.component.get()[-1]
cloneid = clone['id']
bps.testmodel.component[cloneid].label.set('clonnedAppsim')
bps.testmodel
#increase steady for all appsim components to 100s
for component in  bps.testmodel.component.get():
    comp_id = component['id']
    bps.testmodel.component[comp_id].rampDist.steady.set('100')

########################################
print("Save test:")
bps.testmodel.saveAs(new_testmodel_name, force = True)

########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 20}])


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=new_testmodel_name, group=20)
run_id = test_id_json["runid"]
print("Test Run Id: %s"%run_id)

print("~Wait for test to begin initialization.")
runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
while (runningTests["initProgress"] == None):
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    print("...")
    time.sleep(1)

print("~Wait for the initialization process ")
init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
while( int(init_progress) <= 100 and runningTests["progress"] == None):
    init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    time.sleep(1)
    print("Initialization progress:   %s%s" % (init_progress, '%'))

print("~Test is running untill 30% progress. Get  l4Stats stats at every 2 seconds.")
progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
while(type(progress) == str and int(progress) <= 30):
    pp(bps.testmodel.realTimeStats(int(run_id), " l4Stats", -1))
    progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
    time.sleep(2)


########################################
print("~Cancel run")
bps.topology.stopRun(run_id)

print("~Wait for the stop completion ")
while 'TEST-%s'%run_id in bps.topology.runningTest.get():
    init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
    time.sleep(1)
    print("stop progress:   %s%s" % (init_progress, '%'))


#getReportContents 1st 'IP Summary' section
contents=bps.reports.getReportContents(runid=run_id)
for section in contents:
    if section['Section Name'] == 'IP Summary':
        print  ("Report result: %s for runid: %s" % (section  ,run_id))
        tabledata = bps.reports.getReportTable(runid=run_id, sectionId=section['Section ID'])
        table_row_count  = len(tabledata[0]['Measurement'])
        for index in range(table_row_count):
            print ("%s: %s " % (tabledata[0]['Measurement'][index], tabledata[1]['Value'][index]) )
        break

#export capture
print ('Exporting the capture for the ports')
for p in port_list:
    print ('Exporting tescap%s.cap....' % p)
    bps.topology.exportCapture('tescap%s.cap' % p ,\
         {"port": p,"slot": slot_number,"dir": "both","size": 100,"start": 0, "sizetype": "megabytes",  "starttype": "megabytes" } )

print "Waiting 5 secs"
time.sleep(5)
########################################
print("Unreserve ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p}])

########################################
print("Session logout")
bps.logout()

