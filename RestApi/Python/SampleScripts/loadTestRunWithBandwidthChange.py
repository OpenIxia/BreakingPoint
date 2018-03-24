import sys

sys.path.insert(0, '../Modules')
from bpsRest import *
from optparse import OptionParser

# Demo 1 Script. This script will perform the following steps:
# 1. Login
# 2. Show current port reservation state and then reserve the ports
# 3. Upload a test - default "Sample_HTTP_B2B.bpt"
# 4. Change the percentage of the total bandwidth of the test
# 5. Run the loaded test
#   4.a Show progress and test statistics
#   4.b After test completion, show the test result (Pass/Fail)
# 6. Unreserve the ports
# 7. Logout

# Input Parameters
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--SCIP', dest="SCIP", type=str, default="10.36.18.45")
    parser.add_option('--User', dest="User", type=str, default="admin")
    parser.add_option('--Passwd', dest="Passwd", type=str, default="admin")
    parser.add_option('--force', dest="force", type=str, default="true")
    parser.add_option('--LoadedTest', dest="LoadedTest", type=str, default="Sample_HTTP_B2B")
    parser.add_option('--Bandwidth', dest="Bandwidth", type=str, default="10")

(options,args) = parser.parse_args()

bps = BPS(options.SCIP,options.User, options.Passwd)
# login
bps.login()
# showing current port reservation state
bps.portsState()
# reserving the ports.
bps.reservePorts(slot = 1, portList = [0,1], group = 1, force = options.force)

# load the test
TestFileName = "%s.bpt" % options.LoadedTest
bptName = os.path.join(os.getcwd(), TestFileName)
bps.uploadBPT(bptName, options.force, False)

# Change the percentage of the total bandwidth of the test
bps.setSharedComponentSettings(options.LoadedTest, bps.createSharedComponentSettingArg("totalBandwidth", options.Bandwidth), False)

# running the loaded test using group 1
# please note the runid generated. It will be used for many more functionalities
runid = bps.runTest(modelname = options.LoadedTest, group = 1)
# showing progress and current statistics
progress = 0
while (progress < 100):
    progress = bps.getRTS(runid)
    time.sleep(4)
# showing the test result (Pass/Fail)
# a sleep is put here because we do not immediately get the test results.
# inserting a sleep to allow for the data to be stored in the database before retrieval
time.sleep(1)
bps.getTestResult(runid)

# unreserving the ports.
bps.unreservePorts(slot = 1, portList = [0,1], enableRequestPrints = False)

# logging out
bps.logout()
