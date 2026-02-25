# Version of the package
__version__ = "26.0.6"
URL = "https://github.com/OpenIxia/BreakingPoint"

import sys,os
if sys.version_info[0] >= 3:
    from .restPyWrapper3 import BPS, pp
    from .bps_restpy_v1.bpsAdminRest import BPS_Updates, BPS_Storrage
    from .bps_restpy_v1.bpsVEAdminRest import BPSVEAdmin
else:
    from restPyWrapper import BPS, pp
    from bps_restpy_v1.bpsAdminRest import BPS_Updates, BPS_Storrage
    from bps_restpy_v1.bpsVEAdminRest import BPSVEAdmin

BPS_samples = []
samples = os.path.join(__path__[0], 'rest_samples')
for m in os.listdir(samples):
    if m.startswith('__'): continue
    BPS_samples.append(os.path.join(samples, m))
