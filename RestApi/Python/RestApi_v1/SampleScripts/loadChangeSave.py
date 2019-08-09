import sys

sys.path.insert(0, '../Modules')
from BpsRestApi import *
from optparse import OptionParser

# Demo 1 Script. This script will perform the following steps:
# 1. Login
# 2. Upload a test - default "Sample_HTTP_Security.bpt"
# 3. Change the test to disable the Security component
# 4. Save the modified test to a named "Sample_HTTP_Only.bpt"
# 5. Logout

# Input Parameters
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--SCIP', dest="SCIP", type=str, default="10.36.18.45")
    parser.add_option('--User', dest="User", type=str, default="admin")
    parser.add_option('--Passwd', dest="Passwd", type=str, default="admin")
    parser.add_option('--force', dest="force", type=str, default="true")
    parser.add_option('--LoadedTest', dest="LoadedTest", type=str, default="Sample_HTTP_Security")
    parser.add_option('--ModifiedTest', dest="ModifiedTest", type=str, default="Sample_HTTP_only")

(options,args) = parser.parse_args()

bps = BPS(options.SCIP,options.User, options.Passwd)
# login
bps.login()

# load the NN template
TestFileName = "%s.bpt" % options.LoadedTest
bptName = os.path.join(os.getcwd(), TestFileName)
bps.uploadBPT(bptName, options.force, False)

# Disable the security component
bps.modifyNormalTest("security_1", "active", "false", False)

# Save the modified test
bps.saveasNormalTest(options.ModifiedTest, "true", False)
bps.exportTestBPT(options.ModifiedTest, None, options.ModifiedTest, './/', False)

# logging out
bps.logout()
