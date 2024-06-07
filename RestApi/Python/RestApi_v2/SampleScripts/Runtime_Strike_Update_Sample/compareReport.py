import sys, os, time, re, copy
from ReportContent import ReportContent
sys.path.append(os.path.dirname(__file__))
# Harness variables *****************************************
from restPyWrapper3 import *
from collections import defaultdict
if 'py' not in dir():
    class TestFailedError(Exception):
        pass
    class Py:
        pass
    py = Py()
    py.bpsuser = 'admin'
    py.bpspass = 'admin'
    py.ports = [('<IP adddress>', 4, 0), ('<IP adddress>', 4, 1)]

py.bpssys = py.ports[0][0]
# END Harness variables *************************************

########################################
test_model_name = "<test model name>"
testGroup = 20
slot_number = py.ports[0][1]
port_list   = [port[2] for port in py.ports]

########################################
# Login to BPS box
bps = BPS(py.bpssys, py.bpsuser, py.bpspass)
bps.login()
# bpt_file = os.path.join(os.path.dirname(__file__),"s06_security_rest_example.bpt")
bpt_file = os.path.join(os.path.dirname(__file__),"Stan_All_Strikes_All_Variants.bpt")
bps.testmodel.importModel(name=test_model_name,filename=bpt_file, force=True)
bps.testmodel.load(test_model_name)
    
########################################
if __name__ == "__main__":
    try:
        for p in port_list:
            bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': testGroup, 'capture': False}])
        # l47_resource = [0,1]
        # for r in l47_resource:
        #     bps.topology.reserveResource(group = testGroup, resourceId = r, resourceType = "l47")
        print("Run test and Get Stats:")
        test_id_json = bps.testmodel.run(modelname=test_model_name, group=testGroup, allowMalware=True)
        run_id = test_id_json["runid"]
        print("Test Run Id: %s"%run_id)

        print("~Wait for test to begin initialization.")
        runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
        while (type(runningTests) == dict and runningTests["initProgress"] == None):
            runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
            print("...", end="\r")
            time.sleep(1)

        print("~Wait for the initialization process ")
        init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
        while( type(init_progress) == "str" and int(init_progress) <= 100 and runningTests["progress"] == None):
            init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
            runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
            time.sleep(1)
            print("Initialization progress:   %s%s" % (init_progress, '%'))

        print("~Test is running untill 100% progress. Get  l4Stats stats at every 2 seconds.")
        progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
        report_prev = None
        while(type(progress) == int and int(progress) <= 100):
            print(bps.testmodel.realTimeStats(int(run_id), "summary", -1))
            print("===============================================================")
            progress = bps.topology.runningTest['TEST-%s'%run_id].progress.get()
            try:
                report_curr = ReportContent(bps, run_id,security=True)
                report_curr.create_content()
                report_curr.load_all_section()
                if report_prev:
                    report_curr.compare_reportContent(report_prev)
                report_prev = report_curr
                time.sleep(4) 
            except Exception as err:
                if "Internal Server Error" in str(err):
                    print("Server is busy.. back off for 1 minute and retry")
                    for i in range(60, 0, -1):
                        time.sleep(1)
                        print("Retry in {0} s".format(i), end = '\r')
                    continue
                else:
                    raise Exception(str(err))
                           
        
    except Exception as err:
        bps.logout()
        raise Exception(str(err))
       
        
    ######################################
    print("Unreserve ports")
    for p in port_list:
        bps.topology.unreserve([{'slot': slot_number, 'port': p}])
    # print("Unreserving resources")
    # for r in l47_resource:
    #     bps.topology.releaseResource(group = testGroup, resourceId = r, resourceType = "l47")
    print("Session logout") 
    bps.logout()

