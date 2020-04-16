# Title:  Python Script made to create a Test Model from scratch.
# Date:   April 2019
# Author: Maria Turcu
# Actions:
#   1. Login to BPS box
#   2. Create a new smart strike list
#   3. List the strikes from the smart strikelist 
#   4. Create a new strike list
#   5. Add a few strikes
#   6. Remove a strike
#   7. Save As/ Save the strike list
#   8. reserve ports and run
#   9. Monitor security stats
#   10. get results from report section
#   12. Unreserve ports and logout


# Import BPSv2 python library from outside the folder with samples.

########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
# Demo script global variables
new_strikeList_name = "CreatedStrikeList"
new_smart_strikeList_name = "CreatedStrikeList"
new_testmodel_name  = "s06_security_rest_example"
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
# # # STRIKELIST
########################################

print("Create a new smart strike list from scratch with no name.")
bps.strikeList.new()
print("Add Strikes based on the query : year:2019 severity:'High' c2s")
bps.strikeList.queryString.set("year:2019 severity:'High' c2s")

print("Save the smart strike list unde a new name.")
bps.strikeList.saveAs(new_smart_strikeList_name, True)
print ("The contents of the smart strikelist are:")
for strike in bps.strikeList.strikes.get():
    print ("%s : %s" %(strike['category'], strike['name']))

print("Create a new strike list from scratch with no name.")
bps.strikeList.new()

print("Save the strike list unde a new name.")
bps.strikeList.saveAs(new_strikeList_name, True)

print("Add a strike using its path.")
bps.strikeList.add(
    [{"id": "/strikes/exploits/webapp/exec/cve_2018_8007_couchdb_rce.xml"}])

print("Save the current strike list using its name.")
bps.strikeList.save()

print("Add a list of strikes.")
bps.strikeList.add([{"id": "/strikes/malware/malware_e26eeed42cd54e359dae49bd0ae48a3c.xml"}, {
                           "id": "/strikes/exploits/scada/7t_scada_dir_traversal_file_read_write.xml"}])

print("Save the strike list.")
bps.strikeList.save()

print("Remove a strike.")
bps.strikeList.remove(
    [{"id": "/strikes/exploits/webapp/exec/cve_2018_8007_couchdb_rce.xml"}])

print("Save the strike list.")

strikesMatches = bps.strikes.search("apache", limit=10,sort="",sortorder ="",offset="")
strikeListToAdd = []
for strike in strikesMatches:
    print ("Preparing to add: %s %s %s" % (strike['category'], strike['year'], strike['name'] ) )
    strikeListToAdd.append({"id": strike['path']})

bps.strikeList.add(strikeListToAdd)

bps.strikeList.save()

print ("Create a new testmodel to use the newly created strikes")
bps.testmodel.new()
print('Adding an security component ')
bps.testmodel.add(name='restSample_security', type='security_all', active=True, component='security')
print('Configure with the created strikelist ')
pset={"attackPlan": new_strikeList_name, "attackPlanIterations": 12}

#get the id of the 1st component
cmpid = bps.testmodel.component.get()[0]['id']
#set the profile on the component
bps.testmodel.component[cmpid].patch(pset)


bps.testmodel.saveAs(new_testmodel_name, force = True)

########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=new_testmodel_name, group=2)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
print("Test Run Id: %s"%run_id)

#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
while run_id in runningTests_Ids:
     run_state =  bps.topology.runningTest[run_id].get()
     #print progress if test started
     try:
        #print ('progress: %s%% , runtime %ss' % (run_state['progress'], run_state['runtime'] ))
        pp(bps.testmodel.realTimeStats(int(testid), "attackStats", -1))
     except: print ("Starting...")
     time.sleep(2)
     #update the current running tests
     runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 

print("~The test finished the execution.")
results = bps.reports.search(searchString=new_testmodel_name, limit=10, sort="endTime", sortorder="descending")
result  = results[0]
print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)

print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()
