import sys

sys.path.insert(0, '../Modules')
from bpsRest import *

# Demo 1 Script. This script will print out the current state of the ports in JSON format:
# 1. Login
# 2. Print out ports states in JSON format
# 3. Logout

bps = BPS('10.36.18.45', 'admin', 'admin')

# login
bps.login()

# showing current port reservation state
bps.portsStateJson(enableRequestPrints="True")

# logging out
bps.logout()
