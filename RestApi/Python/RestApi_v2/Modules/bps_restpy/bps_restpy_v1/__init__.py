# Version of the package
__version__ = "1.0.6"
URL = "https://github.com/OpenIxia/BreakingPoint"

import sys,os
if sys.version_info[0] >= 3:
    from .bpsRest import BPS
else:
    from bpsRest import BPS

BPS_samples_v1 = []

samples = os.path.join(__path__[0], 'restv1_samples')
for m in os.listdir(samples):
    if m.startswith('__'): continue
    BPS_samples_v1.append(os.path.join(samples, m))