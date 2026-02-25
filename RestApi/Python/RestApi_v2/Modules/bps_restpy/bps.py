# Version of the package
__version__ = "1.0.9"
URL = "https://github.com/OpenIxia/BreakingPoint"

import sys,os
if sys.version_info[0] >= 3:
    from .restPyWrapper3 import BPS, pp
    from .bps_restpy_v1.bpsAdminRest import BPS_Updates, BPS_Storrage
    from .bps_restpy_v1.bpsVEAdminRest import BPSVEAdmin
    from . import BPS_samples
else:
    from restPyWrapper import BPS, pp
    from bps_restpy_v1.bpsAdminRest import BPS_Updates, BPS_Storrage
    from bps_restpy_v1.bpsVEAdminRest import BPSVEAdmin
    from bps_restpy import BPS_samples
