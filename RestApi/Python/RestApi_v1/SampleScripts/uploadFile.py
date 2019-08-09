import sys

sys.path.insert(0, '../Modules')
from BpsRestApi import *

filePath = 'sample.pcap'

bps = BPS('10.36.18.42', 'admin', 'admin')
bps.login()

bps.uploadCapture(filePath, enableRequestPrints=True, forceOverwrite=False)



