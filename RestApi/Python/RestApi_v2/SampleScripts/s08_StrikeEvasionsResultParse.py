# Title:  Python Script made to monitor strike variants execution in real time.
# Date:   Nov 2019
# Actions:
#   1. Import a test that has the necessary security evasion profile
#   2. Create a smart strikelist
#   3. Create a new test from scratch. (* make sure you choose the correct Network name)
#   4. Run the test
#   5. At each 2 seconds Pull stats and check the report
#   6. The update_strikeResult is used for report check
#              *dynamically check the report sections with variants
#              *in real time evaluates and prints allowed strike variants
#              *in real time updates the status of the strikes
#   7. When test ends print results
#   8. Create a new strike list with the failed strikes
#   9. Create a new test for the failed strikes



# Import BPSv2 python library from outside the folder with samples.

########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp

########################################
import re

# Demo script global variables
new_testmodel_name = 's08_StrikeEvasionsResultParse'
new_strikeList_name                = "StrikeList_" + new_testmodel_name
strikeList_all_allowed_from_results= "StrikeList_allowed_" + new_testmodel_name
testmodel_for_allowed_strikes      = "Strikes_allowed_" + new_testmodel_name
network_configuration              = 'BreakingPoint Switching Minimal'
new_evasion_profile                = 'Evasion_100Variants_' + new_testmodel_name
#bps system info
# bps_system  = '<BPS_BOX_IP/HOSTNAME>'
# bpsuser     = 'bps user'
# bpspass     = 'bps pass'
bps_system  = '10.36.81.89'
bpsuser     = 'admin'
bpspass     = 'admin'

slot_number = 1
port_list   = [0, 4]

########################################
# # # procedure to check the strikes report section and read the tables of data
strikeVaiantResult = {}
def update_strikeResult(run_id, bps):
    global strikeVaiantResult
    contents=bps.reports.getReportContents(runid=run_id)
    for section in contents:
        #looking for 'variants/attack name' pattern
        variantMatch = re.search(r'variants\/(\w+)', section['Section Name'])
        if variantMatch: 
            #reading security variant result from report table
            tabledata = bps.reports.getReportTable(runid=run_id, sectionId=section['Section ID'])
            #skip if tabledata is not populated
            if not tabledata or len(tabledata) < 3:
                continue
            for index in range( len( tabledata[1]['Strike Name'] ) ):
                strike_name   = tabledata[1]['Strike Name'][index]
                strike_time   = tabledata[0]['Time of strike'][index]
                strike_result = tabledata[2]['Strike Result'][index]
                #separating name and variant asuming strikename is '<strike name>-<variant Id>'
                strike_variant = strike_name.split('-')[-1]
                strike_name    = variantMatch.group(1)
                #keep history of strike results allready analyzed
                if not strikeVaiantResult.has_key(strike_name):
                    strikeVaiantResult[strike_name] = {'Allowed' : False}                
                #print only if is a new entry 
                if not strikeVaiantResult[strike_name].has_key(strike_variant):
                    strikeVaiantResult[strike_name][strike_variant] = {'time' : strike_time, 'result' : strike_result}
                    if strike_result == 'Allowed':
                        strikeVaiantResult[strike_name]['Allowed'] = True
                        print ("!*! %s variant: %s  result=%s" % (strike_name, strike_variant, strike_result) )



########################################



########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()

########################################
# # # STRIKELIST
########################################


print("Create a new smart strike list from scratch")
bps.strikeList.new()
strikeToSearch = "year:'2019' AND protocol:'http'"
bps.strikeList.queryString.set(strikeToSearch)

print("Save the strike list unde a new name.")
bps.strikeList.saveAs(new_strikeList_name, True)


print("Created strikelist %s for strikes matching %s:" % (new_strikeList_name, strikeToSearch) )
#List the strikes from strikelist
for strike in bps.strikeList.strikes.get():
    print ("%s %s %s" % (strike['category'], strike['year'], strike['name'] ) )


print ("Create a new testmodel to use the newly created strikes")
bps.testmodel.new()
print ("Set allready defined network configuration: %s" % network_configuration)
bps.testmodel.network.set(network_configuration)
print('Adding a security component ')
bps.testmodel.add(name='security_component', type='security_all', active=True, component='security')


print('Search evasion profile')
evasionSearchResult = bps.evasionProfile.search(searchString = "allvariants", limit="", sort="", sortorder="")
evasionProfileTemplate = evasionSearchResult[0]
print ("Selecting Evasion Profile : %s \n %s" % (evasionProfileTemplate['label'],evasionProfileTemplate['description'] ) )

#configuring evasion profile

#loading avasion profile template
bps.evasionProfile.load(evasionProfileTemplate['name'])
#fidn the options
for setting in bps.evasionProfile.StrikeOptions.getStrikeOptions():
    if setting['name'] == 'Variations':
        break

print ("Availlable option for Strike Varinat testing are: ")
pp (setting['options'])

print ("Choosing variant VariantLimit from the available options")
variations = {
    "VariantTesting": True,
    "TestType": "VariantLimit",
    "Limit": '100'
}
#patch varaint option with multiple parameters
bps.evasionProfile.StrikeOptions.Variations.patch(variations)
#set variant option with multiple parameters
bps.evasionProfile.StrikeOptions.Variations.Shuffle.set(True)

bps.evasionProfile.saveAs(new_evasion_profile, force = True)

print('Configure with strike componenet with the created strikelist and evasions')
pset={"attackPlan": new_strikeList_name, "attackPlanIterations": 1, "attackProfile" : new_evasion_profile}

#get the id of the 1st component
cmpid = bps.testmodel.component.get()[0]['id']
#set the profile on the component
bps.testmodel.component[cmpid].patch(pset)



bps.testmodel.saveAs(new_testmodel_name, force = True)

########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 5}])


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=new_testmodel_name, group=5)
run_id = str( test_id_json["runid"] )
print("Test Run Id: %s"%run_id)

#get the ids for all tests running on the chassis
print ("~Wait for test to begin initialization.")
runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
while (runningTests["initProgress"] == None):
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    print ("...")
    time.sleep(2)

print ("~Wait for the initialization process ")
init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
while( int(init_progress) <= 100 and runningTests["progress"] == None):
    init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    time.sleep(1)
    print ("Initialization progress:   %s%s" % (init_progress, '%') )
    

print ("~Test is running. We will do real time report search in this time and also print attack related stats.")
progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
while(type(progress) == str and int(progress) <= 100):
    print (bps.testmodel.realTimeStats(int(run_id), "attackStats", -1) )
    #check report for failed variants
    update_strikeResult(run_id, bps)
    progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
    time.sleep(2)



print("~The test finished the execution.")
delayForDbUpdate = 10
while delayForDbUpdate > 0:
    try:
        results = bps.reports.search(searchString=new_testmodel_name, limit=10, sort="endTime", sortorder="descending")
        result  = results[0]
        print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )
        break
    except:
        print ("Wait for result to be updated in the BreakingPoint DB....")
        time.sleep(10)
        delayForDbUpdate =delayForDbUpdate-1


print ("*Overall Attack variants reults:")
pp(strikeVaiantResult)


#if there are any attacks that failed we will create an attack list with them. 
#This can be done also during run.
strikeListToAdd = []
for strike_name in strikeVaiantResult.keys():
    strikeresult = strikeVaiantResult[strike_name]
    if strikeresult['Allowed']:
        strikeresult.pop('Allowed')
        print ("Preparing to add failed strike: %s " % (strike_name ) )
        print ("Failed variants: %s " % [v for v in strikeresult if strikeresult[v]['result'] == 'Allowed'] )
        #search the name to get the attack path and add it to list
        bps.strikes.search(strike_name, limit=10,sort="",sortorder ="",offset="")
        strikeListToAdd.append({"id": strike['path']})

if strikeListToAdd:
    print("~Create failed attacks strikelist: %s" % strikeList_all_allowed_from_results)
    bps.strikeList.new()
    bps.strikeList.add(strikeListToAdd)
    bps.strikeList.saveAs(strikeList_all_allowed_from_results, force = True)
    print("~Create a test with the failed attacks: %s" % testmodel_for_allowed_strikes)
    #get the id of the 1st component
    cmpid = bps.testmodel.component.get()[0]['id']
    #set the profile on the component
    bps.testmodel.component[cmpid].attackPlan.set(strikeList_all_allowed_from_results)
    bps.testmodel.saveAs(testmodel_for_allowed_strikes, force = True)
    

print ("Unreserving the ports")
time.sleep(3)
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()
