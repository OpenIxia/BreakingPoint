from BpsRestClient import  *

class BpsApi:
    def __init__(self):
        self.BPSProxy = None
        self.statProxy = None
        self.Group = 1
     
    def _change_group(self, number):
        if number < 1 or number > 12:
            raise AssertionError("Group number must be between 1 and 12")
        self.Group = number
        
    def _check_user_authenticated(self):
        if self.BPSProxy is None:
            raise AssertionError("User must be logged in!")
            
    def _check_keys(self, keys, args):
        for key in keys:
            if not key in args:
                raise AssertionError("Parameter %s not found!" %key)        

    def login(self, **kwargs):        
        self._check_keys(['chassis','username','password'], kwargs)
        chassis = kwargs['chassis']
        username = kwargs['username']
        password = kwargs['password']
        self.BPSProxy = BPS(chassis, username, password)
        self.statProxy = StatProxy(self.BPSProxy)
        self.BPSProxy.login()

    def logout(self):
        self._check_user_authenticated()
        self.BPSProxy.logout()        

    def upload_config(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['filename','force'], kwargs)
        filename = kwargs['filename']
        force = kwargs['force']
        if not os.path.isfile(filename):
            raise AssertionError("File %s does not exist!" %filename)
        result = self.BPSProxy.uploadBPT(filename,force)
        if result is None:
            raise AssertionError("Upload failed for file %s" %filename)
        return result
        
    def download_config(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['filename','directory'], kwargs)
        filename = kwargs['filename']
        directory = kwargs['directory']
        if not os.path.isdir(directory):
            os.makedirs(directory)
        test = None
        key = 'testid'
        if key in kwargs:
            test = kwargs[key]        
            self.BPSProxy.exportTestBPT(filename,testId = test, location = directory)            
        else:
            key = 'testname'
            if key in kwargs:
                test = kwargs[key]        
                self.BPSProxy.exportTestBPT(filename,testName = test, location = directory)
            else:
                raise AssertionError("No test id or test name has been provided!")
            
    def reserve_ports(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['slot','portlist','force'], kwargs)
        slot = kwargs['slot']
        portList = kwargs['portlist']
        force = kwargs['force']
        self.BPSProxy.reservePorts(slot,portList,self.Group,force)

    def unreserve_ports(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['slot','portlist'], kwargs)
        slot = kwargs['slot']
        portList = kwargs['portlist']
        self.BPSProxy.unreservePorts(slot,portList)        

    def run_test(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testname'], kwargs)
        testname = kwargs['testname']
        testid = self.BPSProxy.runTest(testname,self.Group)
        if testid == -1:
            raise AssertionError("Failed to run test %s" %testname)
        return testid

    def stop_test(self, **kwargs):
        self._check_user_authenticated()
        testId = None
        key = 'testid'
        if key in kwargs:
            testId = kwargs[key]
        self.BPSProxy.stopTest(testId)

    def get_test_progress(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testid'], kwargs)
        testid = kwargs['testid']
        return self.statProxy.GetTestProgress(testid)

    def get_test_result(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testid'], kwargs)
        testid = kwargs['testid']
        return self.BPSProxy.getTestResult(testid)
    
    def check_test_result(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testid'], kwargs)
        testid = kwargs['testid']
        result = self.get_test_result(**{'testid':testid})   
        if 'fail' in result:
            faildescription = self.BPSProxy.getTestFailureDescription(testid)
            raise AssertionError(faildescription)    
            
    def download_report(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testid','reportname','location'], kwargs)
        testid = kwargs['testid']
        reportname = kwargs['reportname']
        location = kwargs['location']
        self.BPSProxy.exportTestReport(testid, reportname, location)

    def add_stat_watch(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['statname'], kwargs)
        stat = kwargs['statname']
        self.statProxy.AddStatWatch(stat)
        
    def remove_stat_watch(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['statname'], kwargs)
        stat = kwargs['statname']
        self.statProxy.RemoveStatWatch(stat)
        
    def watch_stats(self, **kwargs):
        self._check_user_authenticated()
        self._check_keys(['testid'], kwargs)
        testid = kwargs['testid']
        stats = self.statProxy.GetRegisteredStats(testid)
        statJson = json.dumps(stats)  
        return statJson
