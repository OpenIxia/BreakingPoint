import requests
import json
import pprint
import base64
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=1).pprint


class TlsAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block)

### this BPS REST API wrapper is generated for version: 10.30
class BPS(object):

    def __init__(self, host, user, password, checkVersion=True):
        self.host = host
        self.user = user
        self.password = password
        self.sessionId = None
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter())
        self.clientVersion = BPS.__lver('10.30')
        self.serverVersions = None
        self.checkVersion = checkVersion
        self.printRequests = False
        self.reports = DataModelProxy(wrapper=self, name='reports')
        self.statistics = DataModelProxy(wrapper=self, name='statistics')
        self.administration = DataModelProxy(wrapper=self, name='administration')
        self.superflow = DataModelProxy(wrapper=self, name='superflow')
        self.network = DataModelProxy(wrapper=self, name='network')
        self.appProfile = DataModelProxy(wrapper=self, name='appProfile')
        self.capture = DataModelProxy(wrapper=self, name='capture')
        self.testmodel = DataModelProxy(wrapper=self, name='testmodel')
        self.strikeList = DataModelProxy(wrapper=self, name='strikeList')
        self.evasionProfile = DataModelProxy(wrapper=self, name='evasionProfile')
        self.topology = DataModelProxy(wrapper=self, name='topology')
        self.loadProfile = DataModelProxy(wrapper=self, name='loadProfile')
        self.strikes = DataModelProxy(wrapper=self, name='strikes')
        self.results = DataModelProxy(wrapper=self, name='results')
        self.remote = DataModelProxy(wrapper=self, name='remote')

    ### connect to the system
    def __connect(self):
        r = self.session.post(url='https://' + self.host + '/bps/api/v1/auth/session', data=json.dumps({'username': self.user, 'password': self.password}), headers={'content-type': 'application/json'}, verify=False)
        if(r.status_code == 200):
            self.sessionId = r.json().get('sessionId')
            self.session.headers['sessionId'] = r.json().get('sessionId')
            self.session.headers['X-API-KEY'] = r.json().get('apiKey')
            print('Successfully connected to %s.' % self.host)
        else:
            raise Exception('Failed connecting to %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### Get from data model
    def __delete(self, path):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/'+ path
        headers = {'content-type': 'application/json'}
        if self.printRequests:
            import re
            print("DELETE, %s, h=%s" %(re.sub(".*/bps/api/v2/core/", "", requestUrl), json.dumps(headers)))
        r = self.session.delete(url=requestUrl, headers=headers, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### disconnect from the system
    def __disconnect(self):
        r = self.session.delete(url='https://' + self.host + '/bps/api/v1/auth/session', verify=False)
        if(r.status_code == 204):
            self.sessionId = None
            if 'sessionId' in self.session.headers:
                del self.session.headers['sessionId']
                del self.session.headers['X-API-KEY']
            #print('Successfully disconnected from %s.' % self.host)
        else:
            raise Exception('Failed disconnecting from %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### generic post operation
    def __export(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        if self.printRequests:
            import re
            print("POST, %s, h=%s, d=%s" %(re.sub(".*/bps/api/v2/core/", "", requestUrl), json.dumps(headers), json.dumps(kwargs)))
        r = self.session.post(url=requestUrl, headers={'content-type': 'application/json'}, data=json.dumps(kwargs), verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code == 200) or r.status_code == 204:
            get_url = 'https://' + self.host + r.content.decode()
            get_head = {'content-type': 'application/json'}
            get_req = self.session.get(url = get_url, verify = False, headers = get_head)
            with open(kwargs['filepath'], 'wb') as fd:
                for chunk in get_req.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            get_req.close()
            return {'status_code': r.status_code, 'content': 'success'}
        else:
            raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def __get(self, path, responseDepth=None, **kwargs):
        requestUrl = 'https://%s/bps/api/v2/core%s%s' % (self.host, path, '?responseDepth=%s' % responseDepth if responseDepth else '')
        for key, value in kwargs.items():
            requestUrl = requestUrl + "&%s=%s" % (key, value)
        headers = {'content-type': 'application/json'}
        if self.printRequests:
            import re
            print("GET, %s, %s" %(re.sub(".*/bps/api/v2/core/", "", requestUrl), json.dumps(headers)))
        r = self.session.get(url=requestUrl, headers=headers, verify=False)
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### generic import operation
    def __import(self, path, filename, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        files = {'file': (kwargs['name'], open(filename, 'rb'), 'application/xml')}
        data = {'fileInfo':str(kwargs)}
        if self.printRequests:
            import re
            print("POST, %s, h=%s, d=%s" %(re.sub(".*/bps/api/v2/core/", "", requestUrl), json.dumps(headers), json.dumps(data)))
        r = self.session.post(url=requestUrl, files=files, data=data, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    def __json_load(self, r):
        try:
            return r.json()
        except:
            return r.content.decode() if r.content is not None else None

    @staticmethod
    def __lver(v, count=2):
        x = [0, 0]
        p = lambda s: int(s) if s.isdigit() else -1
        try:
            z = [a for a in map(p, (v.split(".")[:count]))]; x[:len(z)] = z
            x[:len(z)] = z
        except:
            pass
        return x

    ### OPTIONS request
    def __options(self, path):
        r = self.session.options('https://' + self.host + '/bps/api/v2/core/'+ path)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def __patch(self, path, value):
        headers = {'content-type': 'application/json'}
        if self.printRequests:
            print("patch, %s, h=%s, d=%s" %(path, json.dumps(headers), json.dumps(value)))
        r = self.session.patch(url='https://' + self.host + '/bps/api/v2/core/' + path, headers=headers, data=json.dumps(value), verify=False)
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### generic post operation
    def __post(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        headers = {'content-type': 'application/json'}
        if self.printRequests:
            print("POST, %s, h=%s, d=%s" %(path, json.dumps(headers), json.dumps(kwargs)))
        r = self.session.post(url=requestUrl, headers=headers, data=json.dumps(kwargs), verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204, 202]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def __put(self, path, value):
        headers = {'content-type': 'application/json'}
        if self.printRequests:
            print("put, %s, h=%s, d=%s" %(path, json.dumps(headers), json.dumps(value)))
        r = self.session.put(url='https://' + self.host + '/bps/api/v2/core/' + path, headers=headers, data=json.dumps(value), verify=False)
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Imports an ATI License file (.lic) on a hardware platform. This operation is NOT recommended to be used on BPS Virtual platforms.
    @staticmethod
    def _administration_atiLicensing_operations_importAtiLicense(self, filename, name):
        """
        Imports an ATI License file (.lic) on a hardware platform. This operation is NOT recommended to be used on BPS Virtual platforms.
        :param filename (string): import file path
        :param name (string): the name of the license file
        """
        return self._wrapper.__import('/administration/atiLicensing/operations/importAtiLicense', **{'filename': filename, 'name': name})

    ### Exports everything including test models, network configurations and others from system.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _administration_operations_exportAllTests(self, filepath):
        """
        Exports everything including test models, network configurations and others from system.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param filepath (string): The local path where to save the compressed file with all the models. The path must contain the file name and extension (.tar.gz): '/d/c/f/AllTests.tar.gz'
        """
        return self._wrapper.__export('/administration/operations/exportAllTests', **{'filepath': filepath})

    ### Imports all test models, actually imports everything from 'exportAllTests'. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _administration_operations_importAllTests(self, name, filename, force):
        """
        Imports all test models, actually imports everything from 'exportAllTests'. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): String name to append to each test name.
        :param filename (string): The file containing the object.
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper.__import('/administration/operations/importAllTests', **{'name': name, 'filename': filename, 'force': force})

    ### null
    @staticmethod
    def _administration_operations_logs(self, error=False, messages=False, web=False, all=False, audit=False, info=False, system=False, lines=20, drop=0):
        """
        :param error (bool):
        :param messages (bool):
        :param web (bool):
        :param all (bool):
        :param audit (bool):
        :param info (bool):
        :param system (bool):
        :param lines (number): number lines to return
        :param drop (number): number lines to drop
        """
        return self._wrapper.__post('/administration/operations/logs', **{'error': error, 'messages': messages, 'web': web, 'all': all, 'audit': audit, 'info': info, 'system': system, 'lines': lines, 'drop': drop})

    ### close active session
    @staticmethod
    def _administration_sessions_operations_close(self, session):
        """
        close active session
        :param session (string):
        """
        return self._wrapper.__post('/administration/sessions/operations/close', **{'session': session})

    ### list active sessions
    @staticmethod
    def _administration_sessions_operations_list(self):
        """
        list active sessions
        :return result (list):
        """
        return self._wrapper.__post('/administration/sessions/operations/list', **{})

    ### Sets a User Preference.
    @staticmethod
    def _administration_userSettings_operations_changeUserSetting(self, name, value):
        """
        Sets a User Preference.
        :param name (string): The setting name.
        :param value (string): The new value for setting.
        """
        return self._wrapper.__post('/administration/userSettings/operations/changeUserSetting', **{'name': name, 'value': value})

    ### null
    @staticmethod
    def _administration_userSettings_operations_setAutoReserve(self, resourceType, units):
        """
        :param resourceType (string): Valid values: >l47< or >l23<
        :param units (number):
        """
        return self._wrapper.__post('/administration/userSettings/operations/setAutoReserve', **{'resourceType': resourceType, 'units': units})

    ### Adds a list of SuperFlow to the current working Application Profile. ([{'superflow':'adadad', 'weight':'20'},{..}])
    @staticmethod
    def _appProfile_operations_add(self, add):
        """
        Adds a list of SuperFlow to the current working Application Profile. ([{'superflow':'adadad', 'weight':'20'},{..}])
        :param add (list):
               list of object with fields
                      superflow (string): The name of the super flow
                      weight (string): The weight of the super flow
        """
        return self._wrapper.__post('/appProfile/operations/add', **{'add': add})

    ### Deletes a given Application Profile from the database.
    @staticmethod
    def _appProfile_operations_delete(self, name):
        """
        Deletes a given Application Profile from the database.
        :param name (string): The name of the Application Profiles.
        """
        return self._wrapper.__post('/appProfile/operations/delete', **{'name': name})

    ### Exports an Application profile and all of its dependencies.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _appProfile_operations_exportAppProfile(self, name, attachments, filepath):
        """
        Exports an Application profile and all of its dependencies.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the test model to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        """
        return self._wrapper.__export('/appProfile/operations/exportAppProfile', **{'name': name, 'attachments': attachments, 'filepath': filepath})

    ### Imports an application profile, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _appProfile_operations_importAppProfile(self, name, filename, force):
        """
        Imports an application profile, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper.__import('/appProfile/operations/importAppProfile', **{'name': name, 'filename': filename, 'force': force})

    ### Load an existing Application Profile and sets it as the current one.
    @staticmethod
    def _appProfile_operations_load(self, template):
        """
        Load an existing Application Profile and sets it as the current one.
        :param template (string): The name of the template application profile
        """
        return self._wrapper.__post('/appProfile/operations/load', **{'template': template})

    ### Creates a new Application Profile.
    @staticmethod
    def _appProfile_operations_new(self, template=None):
        """
        Creates a new Application Profile.
        :param template (string): This argument must remain unset. Do not set any value for it.
        """
        return self._wrapper.__post('/appProfile/operations/new', **{'template': template})

    ### Recompute percentages in the current working Application Profile
    @staticmethod
    def _appProfile_operations_recompute(self):
        """
        Recompute percentages in the current working Application Profile
        """
        return self._wrapper.__post('/appProfile/operations/recompute', **{})

    ### Removes a SuperFlow from the current working Application Profile.
    @staticmethod
    def _appProfile_operations_remove(self, superflow):
        """
        Removes a SuperFlow from the current working Application Profile.
        :param superflow (string): The name of the super flow.
        """
        return self._wrapper.__post('/appProfile/operations/remove', **{'superflow': superflow})

    ### Saves the current working application profile using the current name. No need to use any parameter.
    @staticmethod
    def _appProfile_operations_save(self, name=None, force=True):
        """
        Saves the current working application profile using the current name. No need to use any parameter.
        :param name (string): The name of the template. No need to configure. The current name is used.
        :param force (bool): Force to save the working Application Profile with the same name. No need to configure. The default is used.
        """
        return self._wrapper.__post('/appProfile/operations/save', **{'name': name, 'force': force})

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _appProfile_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Application Profile
        :param force (bool): Force to save the working Application Profile using the given name.
        """
        return self._wrapper.__post('/appProfile/operations/saveAs', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _appProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search application profile name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :return appprofile (list):
               list of object with fields
                      name (string):
                      label (string):
                      createdBy (string):
                      createdOn (string):
                      revision (number):
                      description (string):
        """
        return self._wrapper.__post('/appProfile/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Imports a capture file to the systemThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _capture_operations_importCapture(self, name, filename, force):
        """
        Imports a capture file to the systemThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the capture being imported
        :param filename (string): The file containing the capture object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper.__import('/capture/operations/importCapture', **{'name': name, 'filename': filename, 'force': force})

    ### null
    @staticmethod
    def _capture_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search capture name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :return item (list):
               list of object with fields
                      name (string):
                      totalPackets (string):
                      duration (string):
                      ipv4Packets (string):
                      ipv6Packets (string):
                      avgPacketSize (string):
                      udpPackets (string):
                      contentType (string):
                      pcapFilesize (string):
                      tcpPackets (string):
                      avgFlowLength (string):
        """
        return self._wrapper.__post('/capture/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Retrieves all the security options
    @staticmethod
    def _evasionProfile_StrikeOptions_operations_getStrikeOptions(self):
        """
        Retrieves all the security options
        :return result (list):
        """
        return self._wrapper.__post('/evasionProfile/StrikeOptions/operations/getStrikeOptions', **{})

    ### Deletes a given Evasion Profile from the database.
    @staticmethod
    def _evasionProfile_operations_delete(self, name):
        """
        Deletes a given Evasion Profile from the database.
        :param name (string): The name of the profile to delete.
        """
        return self._wrapper.__post('/evasionProfile/operations/delete', **{'name': name})

    ### Load an existing Evasion Profile and sets it as the current one.
    @staticmethod
    def _evasionProfile_operations_load(self, template):
        """
        Load an existing Evasion Profile and sets it as the current one.
        :param template (string): The name of an Evasion profile template.
        """
        return self._wrapper.__post('/evasionProfile/operations/load', **{'template': template})

    ### Creates a new Evasion Profile.
    @staticmethod
    def _evasionProfile_operations_new(self, template=None):
        """
        Creates a new Evasion Profile.
        :param template (string): The name should be empty to create a new object.
        """
        return self._wrapper.__post('/evasionProfile/operations/new', **{'template': template})

    ### Saves the working Test Model using the current name. No need to configure. The current name is used.
    @staticmethod
    def _evasionProfile_operations_save(self, name=None, force=True):
        """
        Saves the working Test Model using the current name. No need to configure. The current name is used.
        :param name (string): This argument should be empty for saving the profile using it's actual name.
        :param force (bool): Force to save the working profile with the same name.
        """
        return self._wrapper.__post('/evasionProfile/operations/save', **{'name': name, 'force': force})

    ### Saves the current working Test Model under specified name.
    @staticmethod
    def _evasionProfile_operations_saveAs(self, name, force):
        """
        Saves the current working Test Model under specified name.
        :param name (string): The new name given for the current working Evasion Profile
        :param force (bool): Force to save the working Evasion Profile using a new name.
        """
        return self._wrapper.__post('/evasionProfile/operations/saveAs', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _evasionProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search evasion profile name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by. (name/createdBy ...)
        :param sortorder (string): The sort order (ascending/descending)
        :return attackprofile (list):
               list of object with fields
                      name (string):
                      label (string):
                      createdBy (string):
                      revision (number):
                      description (string):
        """
        return self._wrapper.__post('/evasionProfile/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Create a new custom Load Profile.
    @staticmethod
    def _loadProfile_operations_createNewCustom(self, loadProfile):
        """
        Create a new custom Load Profile.
        :param loadProfile (string): The Name of The load profile object to create.
        """
        return self._wrapper.__post('/loadProfile/operations/createNewCustom', **{'loadProfile': loadProfile})

    ### Deletes a specified load profile from the database.
    @staticmethod
    def _loadProfile_operations_delete(self, name):
        """
        Deletes a specified load profile from the database.
        :param name (string): The name of the loadProfile object to delete.
        """
        return self._wrapper.__post('/loadProfile/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _loadProfile_operations_load(self, template):
        """
        :param template (string):
        """
        return self._wrapper.__post('/loadProfile/operations/load', **{'template': template})

    ### null
    @staticmethod
    def _loadProfile_operations_save(self):
        return self._wrapper.__post('/loadProfile/operations/save', **{})

    ### Save the active editing LoadProfile under specified name
    @staticmethod
    def _loadProfile_operations_saveAs(self, name):
        """
        Save the active editing LoadProfile under specified name
        :param name (string):
        """
        return self._wrapper.__post('/loadProfile/operations/saveAs', **{'name': name})

    ### null
    @staticmethod
    def _loadProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search application profile name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :return loadprofile (list):
               list of object with fields
                      name (string):
                      label (string):
                      createdBy (string):
                      createdOn (string):
                      revision (number):
                      description (string):
        """
        return self._wrapper.__post('/loadProfile/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Adds the given network to the list of most recently opened network configurations.
    @staticmethod
    def _network_operations_addOpenRecent(self, testName):
        """
        Adds the given network to the list of most recently opened network configurations.
        :param testName (object): The test model config
               object of object with fields
                      objectType (string): For network config use: neighborhood
                      name (string):
        """
        return self._wrapper.__post('/network/operations/addOpenRecent', **{'testName': testName})

    ### Deletes a given Network Neighborhood Config from the database.
    @staticmethod
    def _network_operations_delete(self, name):
        """
        Deletes a given Network Neighborhood Config from the database.
        :param name (string): The name of the Network Neighborhood Config.
        """
        return self._wrapper.__post('/network/operations/delete', **{'name': name})

    ### Exports a network neighborhood model in CSV format.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _network_operations_exportCSV(self, name, filepath):
        """
        Exports a network neighborhood model in CSV format.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the network model to be exported.
        :param filepath (string): The local path where to save the exported object.
        """
        return self._wrapper.__export('/network/operations/exportCSV', **{'name': name, 'filepath': filepath})

    ### Export a network neighborhood model in BPT format.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _network_operations_exportNetwork(self, name, attachments, filepath):
        """
        Export a network neighborhood model in BPT format.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the network to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        """
        return self._wrapper.__export('/network/operations/exportNetwork', **{'name': name, 'attachments': attachments, 'filepath': filepath})

    ### Get the most recently opened network configurations
    @staticmethod
    def _network_operations_getRecent(self):
        """
        Get the most recently opened network configurations
        :return recentlyOpened (list):
               list of object with fields
                      objectType (string):
                      name (string):
        """
        return self._wrapper.__post('/network/operations/getRecent', **{})

    ### Imports a network neighborhood model, given as a file.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _network_operations_importNetwork(self, name, filename, force):
        """
        Imports a network neighborhood model, given as a file.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and replace the object having the same name.
        """
        return self._wrapper.__import('/network/operations/importNetwork', **{'name': name, 'filename': filename, 'force': force})

    ### null
    @staticmethod
    def _network_operations_list(self, userid, clazz, sortorder, sort, limit, offset):
        """
        :param userid (string):
        :param clazz (string):
        :param sortorder (string):
        :param sort (string):
        :param limit (number):
        :param offset (number):
        :return returnArg (list):
               list of object with fields
                      name (string):
                      type (string):
                      author (string):
                      createdOn (string):
        """
        return self._wrapper.__post('/network/operations/list', **{'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset})

    ### Loads an existing network config by name.
    @staticmethod
    def _network_operations_load(self, template):
        """
        Loads an existing network config by name.
        :param template (string): The name of the network neighborhood template
        """
        return self._wrapper.__post('/network/operations/load', **{'template': template})

    ### null
    @staticmethod
    def _network_operations_networkInfo(self, name):
        """
        :param name (string):
        :return results (object):
        """
        return self._wrapper.__post('/network/operations/networkInfo', **{'name': name})

    ### Creates a new Network Neighborhood configuration with no name. The template value must remain empty.
    @staticmethod
    def _network_operations_new(self, template=None):
        """
        Creates a new Network Neighborhood configuration with no name. The template value must remain empty.
        :param template (string): The name of the template. In this case will be empty. No need to configure.
        """
        return self._wrapper.__post('/network/operations/new', **{'template': template})

    ### Save the current working network config.
    @staticmethod
    def _network_operations_save(self, name=None, regenerateOldStyle=True, force=True):
        """
        Save the current working network config.
        :param name (string): The new name given for the current working network config. No need to configure. The current name is used.
        :param regenerateOldStyle (bool): No need to configure. The default is used.
        :param force (bool): No need to configure. The default is used.
        """
        return self._wrapper.__post('/network/operations/save', **{'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force})

    ### Saves the working network config and gives it a new name.
    @staticmethod
    def _network_operations_saveAs(self, name, regenerateOldStyle=True, force=False):
        """
        Saves the working network config and gives it a new name.
        :param name (string): The new name given for the current working network config
        :param regenerateOldStyle (bool): Force to apply the changes made on the loaded network configuration. Force to generate a network from the old one.
        :param force (bool): Force to save the network config. It replaces a pre-existing config having the same name.
        """
        return self._wrapper.__post('/network/operations/saveAs', **{'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force})

    ### Search Networks.
    @staticmethod
    def _network_operations_search(self, searchString, userid, clazz, sortorder, sort, limit, offset):
        """
        Search Networks.
        :param searchString (string): Search networks matching the string given.
        :param userid (string): The owner to search for
        :param clazz (string): The 'class' of the object (usually 'canned' or 'custom')
        :param sortorder (string): The order in which to sort: ascending/descending
        :param sort (string): Parameter to sort by: 'name'/'class'/'createdBy'/'interfaces'/'timestamp'
        :param limit (number): The limit of network elements to return
        :param offset (number): The offset to begin from.
        :return network (list):
               list of object with fields
                      name (string):
                      label (string):
                      createdBy (string):
                      revision (number):
                      description (string):
                      type (enum):
        """
        return self._wrapper.__post('/network/operations/search', **{'searchString': searchString, 'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset})

    ### Connects to a remote chassis in order to use some of its resources.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _remote_operations_connectChassis(self, address, remote):
        """
        Connects to a remote chassis in order to use some of its resources.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param address (string): Local chassis address.
        :param remote (string): remote chassis address.
        """
        return self._wrapper.__post('/remote/operations/connectChassis', **{'address': address, 'remote': remote})

    ### Disconnects from a remote chassis in order to release remote resources.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _remote_operations_disconnectChassis(self, address, port):
        """
        Disconnects from a remote chassis in order to release remote resources.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param address (string): Remote chassis address.
        :param port (number): Remote connection port.
        """
        return self._wrapper.__post('/remote/operations/disconnectChassis', **{'address': address, 'port': port})

    ### Deletes a Test Report from the database.
    @staticmethod
    def _reports_operations_delete(self, runid):
        """
        Deletes a Test Report from the database.
        :param runid (number): The test run id that generated the report you want to delete.
        """
        return self._wrapper.__post('/reports/operations/delete', **{'runid': runid})

    ### Exports the result report of a test, identified by its run id and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _reports_operations_exportReport(self, filepath, runid, reportType, sectionIds='', dataType='ALL'):
        """
        Exports the result report of a test, identified by its run id and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param filepath (string): The local path where to export the report, including the report name and proper file extension.
        :param runid (number): Test RUN ID
        :param reportType (string): Report file format to be exported in.Supported types: gwt, csv, pdf, xls, rtf, html, zip, score_img, user_img, xml, stats. For exporting 'extended stats' use 'stats'and use '.zip' as file extension in 'filepath'.
        :param sectionIds (string): Chapter Ids. Can be extracted a chapter or many, a sub-chapter or many or the entire report: (sectionIds='6' / sectionIds='5,6,7' / sectionIds='7.4,8.5.2,8.6.3.1' / sectionIds=''(to export the entire report))
        :param dataType (string): Report content data type to export. Default value is 'all data'. For tabular only use 'TABLE' and for graphs only use 'CHARTS'.
        """
        return self._wrapper.__export('/reports/operations/exportReport', **{'filepath': filepath, 'runid': runid, 'reportType': reportType, 'sectionIds': sectionIds, 'dataType': dataType})

    ### Returns the report Table of Contents using the test run id.
    @staticmethod
    def _reports_operations_getReportContents(self, runid, getTableOfContents=True):
        """
        Returns the report Table of Contents using the test run id.
        :param runid (number): The test run id.
        :param getTableOfContents (bool): Boolean value having the default value set on 'True'. To obtain the Table Contents this value should remain on 'True'.
        :return results (list):
               list of object with fields
                      Section Name (string):
                      Section ID (string):
        """
        return self._wrapper.__post('/reports/operations/getReportContents', **{'runid': runid, 'getTableOfContents': getTableOfContents})

    ### Returns the section of a report
    @staticmethod
    def _reports_operations_getReportTable(self, runid, sectionId):
        """
        Returns the section of a report
        :param runid (number): The test run id.
        :param sectionId (string): The section id of the table desired to extract.
        :return results (object):
        """
        return self._wrapper.__post('/reports/operations/getReportTable', **{'runid': runid, 'sectionId': sectionId})

    ### null
    @staticmethod
    def _reports_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search test name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by: 'name'/'endTime'/'duration'/'result'/'startTime'/'iteration'/'network'/'dut'/'user'/'size'
        :param sortorder (string): The sort order: ascending/descending
        """
        return self._wrapper.__post('/reports/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Returns main groups of statistics for a single BPS Test Component. These groups can be used then in requesting statistics values from the history of a test run.
    @staticmethod
    def _results_operations_getGroups(self, name, dynamicEnums=True, includeOutputs=True):
        """
        Returns main groups of statistics for a single BPS Test Component. These groups can be used then in requesting statistics values from the history of a test run.
        :param name (string): BPS Component name. This argument is actually the component type which can be get from 'statistics' table
        :param dynamicEnums (bool):
        :param includeOutputs (bool):
        :return results (object):
               object of object with fields
                      name (string):
                      label (string):
                      groups (list):
        """
        return self._wrapper.__post('/results/operations/getGroups', **{'name': name, 'dynamicEnums': dynamicEnums, 'includeOutputs': includeOutputs})

    ### null
    @staticmethod
    def _results_operations_getHistoricalResultSize(self, runid, componentid, group):
        """
        :param runid (number): The test run id
        :param componentid (string): The component identifier
        :param group (string): The data group or one of the BPS component main groups. The group name can be get by executing the operation 'getGroups' from results node
        :return result (string):
        """
        return self._wrapper.__post('/results/operations/getHistoricalResultSize', **{'runid': runid, 'componentid': componentid, 'group': group})

    ### Returns stats series for a given component group stat output for a given timestamp
    @staticmethod
    def _results_operations_getHistoricalSeries(self, runid, componentid, dataindex, group):
        """
        Returns stats series for a given component group stat output for a given timestamp
        :param runid (number): The test identifier
        :param componentid (string): The component identifier. Each component has an id and can be get loading the testand checking it's components info
        :param dataindex (number): The table index, equivalent with timestamp.
        :param group (string): The data group or one of the BPS component main groups. The group name can be get by executing the operation 'getGroups' from results node.
        :return param (list):
               list of object with fields
                      name (string):
                      content (string):
                      datasetvals (string):
        """
        return self._wrapper.__post('/results/operations/getHistoricalSeries', **{'runid': runid, 'componentid': componentid, 'dataindex': dataindex, 'group': group})

    ### Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
    @staticmethod
    def _strikeList_operations_add(self, strike, validate=True, toList=None):
        """
        Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
        :param strike (list): The list of strikes to add.
               list of object with fields
                      id (string): Strike path.
        :param validate (bool): Validate the strikes in the given list.
        :param toList (string): All provided strikes will be added to this list. If not existing it will be created
        """
        return self._wrapper.__post('/strikeList/operations/add', **{'strike': strike, 'validate': validate, 'toList': toList})

    ### Deletes a given Strike List from the database.
    @staticmethod
    def _strikeList_operations_delete(self, name):
        """
        Deletes a given Strike List from the database.
        :param name (string): The name of the Strike List to be deleted.
        """
        return self._wrapper.__post('/strikeList/operations/delete', **{'name': name})

    ### Exports the Strike List identified by its name and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _strikeList_operations_exportStrikeList(self, name, filepath):
        """
        Exports the Strike List identified by its name and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the strike list to be exported.
        :param filepath (string): The local path where to save the exported object. The file should have .bap extension
        """
        return self._wrapper.__export('/strikeList/operations/exportStrikeList', **{'name': name, 'filepath': filepath})

    ### Imports a list of strikes residing in a file.
    @staticmethod
    def _strikeList_operations_importStrikeList(self, name, filename, force):
        """
        Imports a list of strikes residing in a file.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object to be imported.
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper.__import('/strikeList/operations/importStrikeList', **{'name': name, 'filename': filename, 'force': force})

    ### Load an existing Strike List and sets it as the current one.
    @staticmethod
    def _strikeList_operations_load(self, template):
        """
        Load an existing Strike List and sets it as the current one.
        :param template (string): The name of the Strike List template
        """
        return self._wrapper.__post('/strikeList/operations/load', **{'template': template})

    ### Creates a new Strike List.
    @staticmethod
    def _strikeList_operations_new(self, template=None):
        """
        Creates a new Strike List.
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper.__post('/strikeList/operations/new', **{'template': template})

    ### Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
    @staticmethod
    def _strikeList_operations_remove(self, strike):
        """
        Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
        :param strike (list): The list of strike ids to remove. The strike id is in fact the it's path.
               list of object with fields
                      id (string):
        """
        return self._wrapper.__post('/strikeList/operations/remove', **{'strike': strike})

    ### Saves the current working Strike List using the current name
    @staticmethod
    def _strikeList_operations_save(self, name=None, force=True):
        """
        Saves the current working Strike List using the current name
        :param name (string): The name of the template. Default is empty.
        :param force (bool): Force to save the working Strike List with the same name.
        """
        return self._wrapper.__post('/strikeList/operations/save', **{'name': name, 'force': force})

    ### Saves the current working Strike List and gives it a new name.
    @staticmethod
    def _strikeList_operations_saveAs(self, name, force):
        """
        Saves the current working Strike List and gives it a new name.
        :param name (string): The new name given for the current working Strike List
        :param force (bool): Force to save the working Strike List using the given name.
        """
        return self._wrapper.__post('/strikeList/operations/saveAs', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _strikeList_operations_search(self, searchString='', limit=10, sort='name', sortorder='ascending'):
        """
        :param searchString (string): Search strike list name matching the string given.
        :param limit (number): The limit of rows to return
        :param sort (string): Parameter to sort by. Default is by name.
        :param sortorder (string): The sort order (ascending/descending). Default is ascending.
        """
        return self._wrapper.__post('/strikeList/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Searches a strike inside all BPS strike database.To list all the available strikes, leave the arguments empty.
    @staticmethod
    def _strikes_operations_search(self, searchString='', limit=10, sort='name', sortorder='ascending', offset=0):
        """
        Searches a strike inside all BPS strike database.To list all the available strikes, leave the arguments empty.
        :param searchString (string): The string used as a criteria to search a strike by.Example: 'strike_name', 'year:2019', 'path:strikes/xml..'
        :param limit (number): The limit of rows to return. Use empty string or empty box to get all the available strikes.
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :param offset (number): The offset to begin from. Default is 0.
        :return strike (list):
               list of object with fields
                      id (string):
                      protocol (string):
                      category (string):
                      direction (string):
                      keyword (string):
                      name (string):
                      path (string):
                      variants (number):
                      severity (string):
                      reference (string):
                      fileSize (string):
                      fileExtension (string):
                      year (string):
        """
        return self._wrapper.__post('/strikes/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder, 'offset': offset})

    ### null
    @staticmethod
    def _superflow_actions_operations_getActionChoices(self, id):
        """
        :param id (number): the flow id
        """
        return self._wrapper.__post('/superflow/actions/operations/getActionChoices', **{'id': id})

    ### Get information about an action in the current working Superflow, retrieving also the choices for each action setting.
    @staticmethod
    def _superflow_actions_operations_getActionInfo(self, id):
        """
        Get information about an action in the current working Superflow, retrieving also the choices for each action setting.
        :param id (number): The action id
        :return result (list):
               list of object with fields
                      label (string):
                      name (string):
                      description (string):
                      choice (object):
        """
        return self._wrapper.__post('/superflow/actions/operations/getActionInfo', **{'id': id})

    ### Gives abbreviated information about all Canned Flow Names.
    @staticmethod
    def _superflow_flows_operations_getCannedFlows(self):
        """
        Gives abbreviated information about all Canned Flow Names.
        :return flow (list):
               list of object with fields
                      name (string):
                      label (string):
        """
        return self._wrapper.__post('/superflow/flows/operations/getCannedFlows', **{})

    ### null
    @staticmethod
    def _superflow_flows_operations_getFlowChoices(self, id, name):
        """
        :param id (number): The flow id.
        :param name (string): The flow type/name.
        :return result (list):
        """
        return self._wrapper.__post('/superflow/flows/operations/getFlowChoices', **{'id': id, 'name': name})

    ### Adds an action to the current working SuperFlow
    @staticmethod
    def _superflow_operations_addAction(self, flowid, type, actionid, source):
        """
        Adds an action to the current working SuperFlow
        :param flowid (number): The flow id.
        :param type (string): The type of the action definition.
        :param actionid (number): The new action id.
        :param source (string): The action source.
        """
        return self._wrapper.__post('/superflow/operations/addAction', **{'flowid': flowid, 'type': type, 'actionid': actionid, 'source': source})

    ### Adds a flow to the current working SuperFlow
    @staticmethod
    def _superflow_operations_addFlow(self, flowParams):
        """
        Adds a flow to the current working SuperFlow
        :param flowParams (object): The flow object to add.
               object of object with fields
                      name (string): The name of the flow
                      from (string): Traffic initiator.
                      to (string): Traffic responder.
        """
        return self._wrapper.__post('/superflow/operations/addFlow', **{'flowParams': flowParams})

    ### Add a host to the current working Superflow
    @staticmethod
    def _superflow_operations_addHost(self, hostParams, force):
        """
        Add a host to the current working Superflow
        :param hostParams (object):
               object of object with fields
                      name (string): The host name.
                      hostname (string): The NickName of the host.
                      iface (string): The traffic direction.Values can be: 'origin'(means client) and 'target'(means server)
        :param force (bool): The flow id.
        """
        return self._wrapper.__post('/superflow/operations/addHost', **{'hostParams': hostParams, 'force': force})

    ### Deletes a given Super Flow from the database.
    @staticmethod
    def _superflow_operations_delete(self, name):
        """
        Deletes a given Super Flow from the database.
        :param name (string): The name of the Super Flow.
        """
        return self._wrapper.__post('/superflow/operations/delete', **{'name': name})

    ### Imports a resource model to be used in flow traffic as .txt files, certificates, keys etc, given as a file. File will be uploaded to '/chroot/resources' by default if 'type' is not specifed otherwise the destination will be '/chroot/resources/'+ (clientcerts / clientkeys / cacerts ...). This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _superflow_operations_importResource(self, name, filename, force, type='resource'):
        """
        Imports a resource model to be used in flow traffic as .txt files, certificates, keys etc, given as a file. File will be uploaded to '/chroot/resources' by default if 'type' is not specifed otherwise the destination will be '/chroot/resources/'+ (clientcerts / clientkeys / cacerts ...). This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        :param type (string): File type to import. Accepted types: clientcert, clientkey, resource, cacert, dhparams. Default value is 'resource'.
        """
        return self._wrapper.__import('/superflow/operations/importResource', **{'name': name, 'filename': filename, 'force': force, 'type': type})

    ### Load an existing Super Flow and sets it as the current one.
    @staticmethod
    def _superflow_operations_load(self, template):
        """
        Load an existing Super Flow and sets it as the current one.
        :param template (string): The name of the existing Super Flow template
        """
        return self._wrapper.__post('/superflow/operations/load', **{'template': template})

    ### Creates a new Super Flow.
    @staticmethod
    def _superflow_operations_new(self, template=None):
        """
        Creates a new Super Flow.
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper.__post('/superflow/operations/new', **{'template': template})

    ### Removes an action from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeAction(self, id):
        """
        Removes an action from the current working SuperFlow.
        :param id (number): The action ID.
        """
        return self._wrapper.__post('/superflow/operations/removeAction', **{'id': id})

    ### Removes a flow from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeFlow(self, id):
        """
        Removes a flow from the current working SuperFlow.
        :param id (number): The flow ID.
        """
        return self._wrapper.__post('/superflow/operations/removeFlow', **{'id': id})

    ### Saves the working Super Flow using the current name
    @staticmethod
    def _superflow_operations_save(self, name=None, force=True):
        """
        Saves the working Super Flow using the current name
        :param name (string): The name of the template that should be empty.
        :param force (bool): Force to save the working Super Flow with the same name.
        """
        return self._wrapper.__post('/superflow/operations/save', **{'name': name, 'force': force})

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _superflow_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Super Flow
        :param force (bool): Force to save the working Super Flow using the given name.
        """
        return self._wrapper.__post('/superflow/operations/saveAs', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _superflow_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search Super Flow name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        """
        return self._wrapper.__post('/superflow/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Lists all the component presets names.
    @staticmethod
    def _testmodel_component_operations_getComponentPreset(self, name='None'):
        """
        Lists all the component presets names.
        :param name (string): The Component type.
        All the component types are listed under the node testComponentTypesDescription.
        If this argument is not set, all the presets will be listed.
        :return component (object):
        """
        return self._wrapper.__post('/testmodel/component/operations/getComponentPreset', **{'name': name})

    ### Lists all the component presets names.
    @staticmethod
    def _testmodel_component_operations_getComponentPresetNames(self, type='None'):
        """
        Lists all the component presets names.
        :param type (string): The Component type.
        All the component types are listed under the node testComponentTypesDescription.
        If this argument is not set, all the presets will be listed.
        :return component (list):
               list of object with fields
                      id (string):
                      label (string):
                      type (string):
                      description (string):
        """
        return self._wrapper.__post('/testmodel/component/operations/getComponentPresetNames', **{'type': type})

    ### Adds a new test component to the current working test model
    @staticmethod
    def _testmodel_operations_add(self, name, component, type, active):
        """
        Adds a new test component to the current working test model
        :param name (string): Component Name
        :param component (string): Component template, preset.
        :param type (string): Component Type: appsim, sesionsender ..
        :param active (bool): Set component enable (by default is active) or disable
        """
        return self._wrapper.__post('/testmodel/operations/add', **{'name': name, 'component': component, 'type': type, 'active': active})

    ### Adds the given test to the list of most recently opened tests.
    @staticmethod
    def _testmodel_operations_addOpenRecent(self, testName):
        """
        Adds the given test to the list of most recently opened tests.
        :param testName (object): The test model config
               object of object with fields
                      objectType (string): For test use: executable
                      name (string):
                      type (string): TEST / PLAN / MULTIBOX
        """
        return self._wrapper.__post('/testmodel/operations/addOpenRecent', **{'testName': testName})

    ### Clones a component in the current working Test Model
    @staticmethod
    def _testmodel_operations_clone(self, template, type, active):
        """
        Clones a component in the current working Test Model
        :param template (string): The ID of the test component to clone.
        :param type (string): Component Type: appsim, sesionsender ..
        :param active (bool): Set component enable (by default is active) or disable
        """
        return self._wrapper.__post('/testmodel/operations/clone', **{'template': template, 'type': type, 'active': active})

    ### Deletes a given Test Model from the database.
    @staticmethod
    def _testmodel_operations_delete(self, name):
        """
        Deletes a given Test Model from the database.
        :param name (string): The name of the Test Model.
        """
        return self._wrapper.__post('/testmodel/operations/delete', **{'name': name})

    ### Exports a wanted test model by giving its name or its test run id.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _testmodel_operations_exportModel(self, name, attachments, filepath, runid=None):
        """
        Exports a wanted test model by giving its name or its test run id.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the test model to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        :param runid (number): Test RUN ID
        """
        return self._wrapper.__export('/testmodel/operations/exportModel', **{'name': name, 'attachments': attachments, 'filepath': filepath, 'runid': runid})

    ### null
    @staticmethod
    def _testmodel_operations_flowExceptions(self, runid, limit, offset):
        """
        :param runid (number): Test RUN ID
        :param limit (number): The limit of rows to return
        :param offset (number): The start row of the returned list
        :return flowException (object):
        """
        return self._wrapper.__post('/testmodel/operations/flowExceptions', **{'runid': runid, 'limit': limit, 'offset': offset})

    ### Get the most recently opened tests
    @staticmethod
    def _testmodel_operations_getRecent(self):
        """
        Get the most recently opened tests
        :return recentlyOpened (list):
               list of object with fields
                      objectType (string):
                      name (string):
                      dut (string):
        """
        return self._wrapper.__post('/testmodel/operations/getRecent', **{})

    ### Imports a test model, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _testmodel_operations_importModel(self, name, filename, force):
        """
        Imports a test model, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper.__import('/testmodel/operations/importModel', **{'name': name, 'filename': filename, 'force': force})

    ### Load an existing test model template.
    @staticmethod
    def _testmodel_operations_load(self, template):
        """
        Load an existing test model template.
        :param template (string): The name of the template testmodel
        """
        return self._wrapper.__post('/testmodel/operations/load', **{'template': template})

    ### Creates a new Test Model
    @staticmethod
    def _testmodel_operations_new(self, template=None):
        """
        Creates a new Test Model
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper.__post('/testmodel/operations/new', **{'template': template})

    ### Retrieves the real time statistics for the running test, by giving the run id.
    @staticmethod
    def _testmodel_operations_realTimeStats(self, runid, rtsgroup, numSeconds, numDataPoints=1):
        """
        Retrieves the real time statistics for the running test, by giving the run id.
        :param runid (number): Test RUN ID
        :param rtsgroup (string): Real Time Stats group name. Values for this can be get from 'statistics' node, inside 'statNames' from each component at 'realtime Group' key/column. Examples: 'l7STats', 'all', 'bpslite', 'summary', 'clientStats' etc.Instead of a group name, it can be used a statistic name and the usage is: `fields:<statname>`Example: 'fields:txFrames' or 'fields:ethTxFrames, appIncomplete, rxFrameRate, etc'.
        :param numSeconds (number): The number of seconds.  If negative, means counting from the end. Example -1 means the last second from the moment of request.
        :param numDataPoints (number): The number of data points, or set of values, on server side. The default is 1. In case of missing stats,because of requesting to many stats per second in real time,increase the value (grater than 1)
        :return result (object):
               object of object with fields
                      testStuck (bool):
                      time (number):
                      progress (number):
                      values (string):
        """
        return self._wrapper.__post('/testmodel/operations/realTimeStats', **{'runid': runid, 'rtsgroup': rtsgroup, 'numSeconds': numSeconds, 'numDataPoints': numDataPoints})

    ### Removes a component from the current working Test Model.
    @staticmethod
    def _testmodel_operations_remove(self, id):
        """
        Removes a component from the current working Test Model.
        :param id (string): The component id.
        """
        return self._wrapper.__post('/testmodel/operations/remove', **{'id': id})

    ### Runs a Test.
    @staticmethod
    def _testmodel_operations_run(self, modelname, group, allowMalware=False):
        """
        Runs a Test.
        :param modelname (string): Test Name to run
        :param group (number): Group to run
        :param allowMalware (bool): Enable this option to allow malware in test.
        """
        return self._wrapper.__post('/testmodel/operations/run', **{'modelname': modelname, 'group': group, 'allowMalware': allowMalware})

    ### Saves the working Test Model using the current name. No need to configure. The current name is used.
    @staticmethod
    def _testmodel_operations_save(self, name=None, force=True):
        """
        Saves the working Test Model using the current name. No need to configure. The current name is used.
        :param name (string): The name of the template that should be empty.
        :param force (bool): Force to save the working Test Model with the same name.
        """
        return self._wrapper.__post('/testmodel/operations/save', **{'name': name, 'force': force})

    ### Saves the current working Test Model under specified name.
    @staticmethod
    def _testmodel_operations_saveAs(self, name, force):
        """
        Saves the current working Test Model under specified name.
        :param name (string): The new name given for the current working Test Model
        :param force (bool): Force to save the working Test Model using a new name.
        """
        return self._wrapper.__post('/testmodel/operations/saveAs', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _testmodel_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search test name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by: 'createdOn'/'timestamp'/'bandwidth'/'result'/'lastrunby'/'createdBy'/'interfaces'/'testLabType'
        :param sortorder (string): The sort order: ascending/descending
        :return testmodel (list):
               list of object with fields
                      name (string):
                      label (string):
                      createdBy (string):
                      network (string):
                      duration (number):
                      description (string):
        """
        return self._wrapper.__post('/testmodel/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Stops the test run.
    @staticmethod
    def _testmodel_operations_stopRun(self, runid):
        """
        Stops the test run.
        :param runid (number): Test RUN ID
        """
        return self._wrapper.__post('/testmodel/operations/stopRun', **{'runid': runid})

    ### Returns main groups of statistics for a single BPS Test Component. These groups can be used then in requesting statistics values from the history of a test run.
    @staticmethod
    def _testmodel_operations_testComponentDefinition(self, name, dynamicEnums=True, includeOutputs=True):
        """
        Returns main groups of statistics for a single BPS Test Component. These groups can be used then in requesting statistics values from the history of a test run.
        :param name (string): BPS Component name. This argument is actually the component type which can be get from 'statistics' table
        :param dynamicEnums (bool):
        :param includeOutputs (bool):
        :return results (object):
        """
        return self._wrapper.__post('/testmodel/operations/testComponentDefinition', **{'name': name, 'dynamicEnums': dynamicEnums, 'includeOutputs': includeOutputs})

    ### null
    @staticmethod
    def _testmodel_operations_validate(self, group):
        """
        :param group (string): The reservation group
        :return check (object):
        """
        return self._wrapper.__post('/testmodel/operations/validate', **{'group': group})

    ### Adds a note to given port.
    @staticmethod
    def _topology_operations_addPortNote(self, interface, note):
        """
        Adds a note to given port.
        :param interface (object): Slot and Port ID.
               object of object with fields
                      slot (number):
                      port (string):
        :param note (string): Note info.
        """
        return self._wrapper.__post('/topology/operations/addPortNote', **{'interface': interface, 'note': note})

    ### Adds a note to given resource.
    @staticmethod
    def _topology_operations_addResourceNote(self, resourceId, resourceType):
        """
        Adds a note to given resource.
        :param resourceId (string): Resource Id.
        :param resourceType (string): Resource type.
        """
        return self._wrapper.__post('/topology/operations/addResourceNote', **{'resourceId': resourceId, 'resourceType': resourceType})

    ### Exports a port capture from a test run.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _topology_operations_exportCapture(self, filepath, args):
        """
        Exports a port capture from a test run.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param filepath (string): The local path where to save the exported object.
        :param args (object): Export filters. The Possible values for: 'dir'(direction) are 'tx','rx','both';for 'sizetype' and 'starttype'(units for size and start) are 'megabytes' or 'frames'
               object of object with fields
                      port (string): Port label
                      slot (number): Slot number
                      dir (string): Capturing direction (rx, tx, both)
                      size (number): The size of the capture to be exported.
                      start (number): Start at point.
                      sizetype (string): The size unit: megabytes or frames.
                      starttype (string): The start unit: megabytes or frames.
        """
        return self._wrapper.__export('/topology/operations/exportCapture', **{'filepath': filepath, 'args': args})

    ### Gets the card Fanout modes of a board.
    @staticmethod
    def _topology_operations_getFanoutModes(self, cardId):
        """
        Gets the card Fanout modes of a board.
        :param cardId (number): Slot ID.
        :return modes (object): Fanout mode id per card type.
        """
        return self._wrapper.__post('/topology/operations/getFanoutModes', **{'cardId': cardId})

    ### Get available port fan-out modes.
    @staticmethod
    def _topology_operations_getPortAvailableModes(self, cardId, port):
        """
        Get available port fan-out modes.
        :param cardId (number): Slot id
        :param port (number): Port id to be interrogated
        :return modes (object): Available port switch modes.
        """
        return self._wrapper.__post('/topology/operations/getPortAvailableModes', **{'cardId': cardId, 'port': port})

    ### Reboots the slot with slotId.
    @staticmethod
    def _topology_operations_reboot(self, board):
        """
        Reboots the slot with slotId.
        :param board (number):
        """
        return self._wrapper.__post('/topology/operations/reboot', **{'board': board})

    ### Reboots the compute node with cnId.
    @staticmethod
    def _topology_operations_rebootComputeNode(self, cnId):
        """
        Reboots the compute node with cnId.
        :param cnId (string): Compute node id
        """
        return self._wrapper.__post('/topology/operations/rebootComputeNode', **{'cnId': cnId})

    ### null
    @staticmethod
    def _topology_operations_releaseAllCnResources(self, cnId):
        """
        :param cnId (string):
        """
        return self._wrapper.__post('/topology/operations/releaseAllCnResources', **{'cnId': cnId})

    ### null
    @staticmethod
    def _topology_operations_releaseResource(self, group, resourceId, resourceType):
        """
        :param group (number):
        :param resourceId (number):
        :param resourceType (string):
        """
        return self._wrapper.__post('/topology/operations/releaseResource', **{'group': group, 'resourceId': resourceId, 'resourceType': resourceType})

    ### null
    @staticmethod
    def _topology_operations_releaseResources(self, count, resourceType, slotId):
        """
        :param count (number):
        :param resourceType (string):
        :param slotId (number):
        """
        return self._wrapper.__post('/topology/operations/releaseResources', **{'count': count, 'resourceType': resourceType, 'slotId': slotId})

    ### null
    @staticmethod
    def _topology_operations_reserve(self, reservation, force=False):
        """
        :param reservation (list): Reserves one or more ports
               list of object with fields
                      group (number):
                      slot (number):
                      port (string):
                      capture (bool):
        :param force (bool):
        """
        return self._wrapper.__post('/topology/operations/reserve', **{'reservation': reservation, 'force': force})

    ### Reserves all l47 resources of given compute node id.
    @staticmethod
    def _topology_operations_reserveAllCnResources(self, group, cnId):
        """
        Reserves all l47 resources of given compute node id.
        :param group (number):
        :param cnId (string):
        """
        return self._wrapper.__post('/topology/operations/reserveAllCnResources', **{'group': group, 'cnId': cnId})

    ### Reserves the specified resource of the given type.
    @staticmethod
    def _topology_operations_reserveResource(self, group, resourceId, resourceType):
        """
        Reserves the specified resource of the given type.
        :param group (number):
        :param resourceId (number):
        :param resourceType (string):
        """
        return self._wrapper.__post('/topology/operations/reserveResource', **{'group': group, 'resourceId': resourceId, 'resourceType': resourceType})

    ### Reserves the specified number of resources of given type.
    @staticmethod
    def _topology_operations_reserveResources(self, group, count, resourceType, slotId):
        """
        Reserves the specified number of resources of given type.
        :param group (number):
        :param count (number):
        :param resourceType (string):
        :param slotId (number):
        """
        return self._wrapper.__post('/topology/operations/reserveResources', **{'group': group, 'count': count, 'resourceType': resourceType, 'slotId': slotId})

    ### Runs a Test.
    @staticmethod
    def _topology_operations_run(self, modelname, group, allowMalware=False):
        """
        Runs a Test.
        :param modelname (string): Test Name to run
        :param group (number): Group to run
        :param allowMalware (bool): Enable this option to allow malware in test.
        """
        return self._wrapper.__post('/topology/operations/run', **{'modelname': modelname, 'group': group, 'allowMalware': allowMalware})

    ### Sets the card fanout of a board
    @staticmethod
    def _topology_operations_setCardFanout(self, board, fanid):
        """
        Sets the card fanout of a board
        :param board (number): Slot ID.
        :param fanid (number): The fan type represented by an integer id.
        		Get card specific fanout modes by calling 'topology.getFanoutModes(<card_id>)'.
        		For CloudStorm: 0(100G), 1(40G), 2(25G), 3(10G), 4(50G).
        		For PerfectStorm 40G: 0(40G), 1(10G).
        		For PerfectStorm 100G: 0(100G), 1(40G), 2(10G)
        """
        return self._wrapper.__post('/topology/operations/setCardFanout', **{'board': board, 'fanid': fanid})

    ### Sets the card mode of a board.
    @staticmethod
    def _topology_operations_setCardMode(self, board, mode):
        """
        Sets the card mode of a board.
        :param board (number): Slot ID.
        :param mode (number): The new mode: 10(BPS-L23), 7(BPS L4-7), 3(IxLoad),
        		11(BPS QT L2-3), 12(BPS QT L4-7)
        """
        return self._wrapper.__post('/topology/operations/setCardMode', **{'board': board, 'mode': mode})

    ### Sets the card speed of a board
    @staticmethod
    def _topology_operations_setCardSpeed(self, board, speed):
        """
        Sets the card speed of a board
        :param board (number): Slot ID.
        :param speed (number): The new speed.(the int value for 1G is 1000, 10G(10000), 40G(40000))
        """
        return self._wrapper.__post('/topology/operations/setCardSpeed', **{'board': board, 'speed': speed})

    ### Enables/Disables the performance acceleration for a BPS VE blade.
    @staticmethod
    def _topology_operations_setPerfAcc(self, board, perfacc):
        """
        Enables/Disables the performance acceleration for a BPS VE blade.
        :param board (number): Slot ID.
        :param perfacc (bool): Boolean value: 'True' to enable the performance Acceleration and 'False' otherwise.
        """
        return self._wrapper.__post('/topology/operations/setPerfAcc', **{'board': board, 'perfacc': perfacc})

    ### Switch port fan-out mode.
    @staticmethod
    def _topology_operations_setPortFanoutMode(self, board, port, mode):
        """
        Switch port fan-out mode.
        :param board (number):
        :param port (string):
        :param mode (string):
        """
        return self._wrapper.__post('/topology/operations/setPortFanoutMode', **{'board': board, 'port': port, 'mode': mode})

    ### null
    @staticmethod
    def _topology_operations_setPortSettings(self, linkState, autoNegotiation, precoder, slotId, portId):
        """
        :param linkState (string):
        :param autoNegotiation (bool):
        :param precoder (bool):
        :param slotId (number):
        :param portId (string):
        """
        return self._wrapper.__post('/topology/operations/setPortSettings', **{'linkState': linkState, 'autoNegotiation': autoNegotiation, 'precoder': precoder, 'slotId': slotId, 'portId': portId})

    ### Reboots the metwork processors on the given card card. Only available for APS cards.
    @staticmethod
    def _topology_operations_softReboot(self, board, cnId):
        """
        Reboots the metwork processors on the given card card. Only available for APS cards.
        :param board (number):
        :param cnId (string):
        """
        return self._wrapper.__post('/topology/operations/softReboot', **{'board': board, 'cnId': cnId})

    ### Stops the test run.
    @staticmethod
    def _topology_operations_stopRun(self, runid):
        """
        Stops the test run.
        :param runid (number): Test RUN ID
        """
        return self._wrapper.__post('/topology/operations/stopRun', **{'runid': runid})

    ### null
    @staticmethod
    def _topology_operations_unreserve(self, unreservation):
        """
        :param unreservation (list):
               list of object with fields
                      slot (number):
                      port (number):
        """
        return self._wrapper.__post('/topology/operations/unreserve', **{'unreservation': unreservation})

    ### login into the bps system
    def login(self, **kwargs):
        self.__connect()
        loginData = {'username': self.user, 'password': self.password, 'sessionId': self.sessionId}
        loginData.update(kwargs)
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/login', data=json.dumps(loginData), headers={'content-type': 'application/json'}, verify=False)
        if(r.status_code == 200):
            self.serverVersions = self.__json_load(r)
            apiServerVersion = BPS.__lver(self.serverVersions['apiServer'] if self.serverVersions and 'apiServer' in self.serverVersions else '0.0')
            if self.checkVersion:
                if apiServerVersion > self.clientVersion:
                    self.logout()
                    #self.printVersions()
                    raise Exception('Keysight Python REST-API Wrapper version is older than the BPS server version.\nThis is not a supported combination.\nPlease use the updated version of the wrapper provided with BPS system.')
                if apiServerVersion < self.clientVersion:
                    print("Warning: Keysight Python REST-API Wrapper version is newer than the BPS server version.\nSome of the functionalities included in the Python wrapper might not be supported by the REST API.")
            #print('Login successful.\nWelcome %s. \nYour session id is %s' % (self.user, self.sessionId))
        else:
            raise Exception('Login failed.\ncode:%s, content:%s' % (r.status_code, r.content))
        return self.serverVersions

    ### logout from the bps system
    def logout(self):
        self.serverVersions = None
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/logout', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        if(r.status_code == 200):
            #print('Logout successful. \nBye %s.' % self.user)
            self.__disconnect()
        else:
            raise Exception('Logout failed: (%s, %s)' % (r.status_code, r.content))

    def printVersions(self):
        apiServerVersion = 'N/A'
        if self.serverVersions != None and 'apiServer' in self.serverVersions:
            apiServerVersion = self.serverVersions['apiServer']
        print('Client version: %s \nServer version: %s' % (self.clientVersion, apiServerVersion))

class DataModelMeta(type):
    _dataModel = {
        'administration': {
            'atiLicensing': {
                'license': [{
                    'boardserialno': {
                    },
                    'expires': {
                    },
                    'issued': {
                    },
                    'issuedBy': {
                    },
                    'maintenance': {
                        'maintenanceExpiration': {
                        }
                    },
                    'name': {
                    },
                    'serialno': {
                    },
                    'slotNo': {
                    }
                }],
                'operations': {
                    'importAtiLicense': [{
                    }]
                }
            },
            'operations': {
                'exportAllTests': [{
                }],
                'importAllTests': [{
                }],
                'logs': [{
                }]
            },
            'sessions': [{
                'age': {
                },
                'dataContext': {
                },
                'inactivity': {
                },
                'inactivityTimeout': {
                },
                'note': {
                },
                'operations': {
                    'close': [{
                    }],
                    'list': [{
                        'age': {
                        },
                        'dataContext': {
                        },
                        'inactivity': {
                        },
                        'inactivityTimeout': {
                        },
                        'note': {
                        },
                        'session': {
                        },
                        'type': {
                        },
                        'user': {
                        }
                    }]
                },
                'session': {
                },
                'type': {
                },
                'user': {
                }
            }],
            'systemSettings': {
                'author': {
                },
                'clazz': {
                },
                'createdBy': {
                },
                'createdOn': {
                },
                'description': {
                },
                'guardrailSettings': {
                    'enableStrictMode': {
                    },
                    'stopOnLinkdown': {
                    },
                    'testStartPrevention': {
                    },
                    'testStatusWarning': {
                    },
                    'testStop': {
                    }
                },
                'label': {
                },
                'lockedBy': {
                },
                'revision': {
                },
                'softwareUpdate': {
                    'check': {
                    },
                    'interval': {
                    },
                    'password': {
                    },
                    'username': {
                    }
                },
                'strikepackUpdate': {
                    'check': {
                    },
                    'interval': {
                    },
                    'password': {
                    },
                    'username': {
                    }
                },
                'vacuumSettings': {
                    'autoVacuum': {
                    },
                    'vacuumWindowHigh': {
                    },
                    'vacuumWindowLow': {
                    },
                    'vacuumWindowTZ': {
                    }
                }
            },
            'userSettings': [{
                'content': {
                },
                'name': {
                },
                'operations': {
                    'changeUserSetting': [{
                    }],
                    'setAutoReserve': [{
                    }]
                }
            }]
        },
        'appProfile': {
            'author': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'operations': {
                'add': [{
                }],
                'delete': [{
                }],
                'exportAppProfile': [{
                }],
                'importAppProfile': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'recompute': [{
                }],
                'remove': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'revision': {
            },
            'superflow': [{
                'author': {
                },
                'clazz': {
                },
                'constraints': {
                },
                'createdBy': {
                },
                'createdOn': {
                },
                'description': {
                },
                'estimate_bytes': {
                },
                'estimate_flows': {
                },
                'generated': {
                },
                'label': {
                },
                'lockedBy': {
                },
                'name': {
                },
                'params': {
                },
                'percentBandwidth': {
                },
                'percentFlows': {
                },
                'revision': {
                },
                'seed': {
                },
                'settings': [{
                    'description': {
                    },
                    'label': {
                    },
                    'name': {
                    },
                    'realtimeGroup': {
                    },
                    'units': {
                    }
                }],
                'weight': {
                }
            }],
            'weightType': {
            }
        },
        'capture': {
            'author': {
            },
            'avgFlowLength': {
            },
            'avgPacketSize': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'duration': {
            },
            'ipv4Packets': {
            },
            'ipv6Packets': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'operations': {
                'importCapture': [{
                }],
                'search': [{
                }]
            },
            'pcapFilesize': {
            },
            'revision': {
            },
            'tcpPackets': {
            },
            'totalPackets': {
            },
            'udpPackets': {
            }
        },
        'evasionProfile': {
            'StrikeOptions': {
                'COMMAND': {
                    'Malicious': {
                    },
                    'PadCommandWhitespace': {
                    },
                    'PadPathSlashes': {
                    }
                },
                'DCERPC': {
                    'MaxFragmentSize': {
                    },
                    'MultiContextBind': {
                    },
                    'MultiContextBindHead': {
                    },
                    'MultiContextBindTail': {
                    },
                    'UseObjectID': {
                    }
                },
                'EMAIL': {
                    'EnvelopeType': {
                    },
                    'From': {
                    },
                    'ShuffleHeaders': {
                    },
                    'To': {
                    }
                },
                'Ethernet': {
                    'MTU': {
                    }
                },
                'FILETRANSFER': {
                    'CompressionMethod': {
                    },
                    'FtpTransferMethod': {
                    },
                    'Imap4Encoding': {
                    },
                    'Pop3Encoding': {
                    },
                    'SmtpEncoding': {
                    },
                    'TransportProtocol': {
                    }
                },
                'FTP': {
                    'AuthenticationType': {
                    },
                    'FTPEvasionLevel': {
                    },
                    'PadCommandWhitespace': {
                    },
                    'Password': {
                    },
                    'Username': {
                    }
                },
                'Global': {
                    'AllowDeprecated': {
                    },
                    'BehaviorOnTimeout': {
                    },
                    'CachePoisoning': {
                    },
                    'FalsePositives': {
                    },
                    'IOTimeout': {
                    },
                    'MaxTimeoutPerStrike': {
                    }
                },
                'HTML': {
                    'HTMLUnicodeEncoding': {
                    },
                    'HTMLUnicodeUTF7EncodingMode': {
                    },
                    'HTMLUnicodeUTF8EncodingMode': {
                    },
                    'HTMLUnicodeUTF8EncodingSize': {
                    }
                },
                'HTTP': {
                    'AuthenticationType': {
                    },
                    'Base64EncodePOSTData': {
                    },
                    'ClientChunkedTransfer': {
                    },
                    'ClientChunkedTransferSize': {
                    },
                    'DirectoryFakeRelative': {
                    },
                    'DirectorySelfReference': {
                    },
                    'EncodeDoubleNibbleHex': {
                    },
                    'EncodeDoublePercentHex': {
                    },
                    'EncodeFirstNibbleHex': {
                    },
                    'EncodeHexAll': {
                    },
                    'EncodeHexRandom': {
                    },
                    'EncodeSecondNibbleHex': {
                    },
                    'EncodeUnicodeAll': {
                    },
                    'EncodeUnicodeBareByte': {
                    },
                    'EncodeUnicodeInvalid': {
                    },
                    'EncodeUnicodePercentU': {
                    },
                    'EncodeUnicodeRandom': {
                    },
                    'EndRequestFakeHTTPHeader': {
                    },
                    'ForwardToBackSlashes': {
                    },
                    'GetParameterRandomPrepend': {
                    },
                    'HTTPServerProfile': {
                    },
                    'HTTPTransportMethods': {
                    },
                    'IgnoreHeaders': {
                    },
                    'MethodRandomInvalid': {
                    },
                    'MethodRandomizeCase': {
                    },
                    'MethodURINull': {
                    },
                    'MethodURISpaces': {
                    },
                    'MethodURITabs': {
                    },
                    'PadHTTPPost': {
                    },
                    'Password': {
                    },
                    'PostParameterRandomPrepend': {
                    },
                    'RequestFullURL': {
                    },
                    'RequireLeadingSlash': {
                    },
                    'ServerChunkedTransfer': {
                    },
                    'ServerChunkedTransferSize': {
                    },
                    'ServerCompression': {
                    },
                    'ShuffleHeaders': {
                    },
                    'URIAppendAltSpaces': {
                    },
                    'URIAppendAltSpacesSize': {
                    },
                    'URIPrependAltSpaces': {
                    },
                    'URIPrependAltSpacesSize': {
                    },
                    'URIRandomizeCase': {
                    },
                    'Username': {
                    },
                    'VersionRandomInvalid': {
                    },
                    'VersionRandomizeCase': {
                    },
                    'VersionUse0_9': {
                    },
                    'VirtualHostname': {
                    },
                    'VirtualHostnameType': {
                    }
                },
                'ICMP': {
                    'DoEcho': {
                    }
                },
                'IMAP4': {
                    'AuthenticationType': {
                    },
                    'IMAPUseProxyMode': {
                    },
                    'Password': {
                    },
                    'Username': {
                    }
                },
                'IP': {
                    'FragEvasion': {
                    },
                    'FragOrder': {
                    },
                    'FragPolicy': {
                    },
                    'IPEvasionsOnBothSides': {
                    },
                    'MaxFragSize': {
                    },
                    'MaxReadSize': {
                    },
                    'MaxWriteSize': {
                    },
                    'RFC3128': {
                    },
                    'RFC3128FakePort': {
                    },
                    'RFC3514': {
                    },
                    'ReadWriteWindowSize': {
                    },
                    'TOS': {
                    },
                    'TTL': {
                    }
                },
                'IPv6': {
                    'TC': {
                    }
                },
                'JAVASCRIPT': {
                    'Encoding': {
                    },
                    'Obfuscate': {
                    }
                },
                'MALWARE': {
                    'CompressionMethod': {
                    },
                    'FilenameInsertEnvVar': {
                    },
                    'FtpTransferMethod': {
                    },
                    'Imap4Encoding': {
                    },
                    'Pop3Encoding': {
                    },
                    'SmtpEncoding': {
                    },
                    'TransportProtocol': {
                    }
                },
                'MS_Exchange_Ports': {
                    'SystemAttendant': {
                    }
                },
                'OLE': {
                    'RefragmentData': {
                    }
                },
                'PDF': {
                    'HexEncodeNames': {
                    },
                    'PreHeaderData': {
                    },
                    'RandomizeDictKeyOrder': {
                    },
                    'ShortFilterNames': {
                    },
                    'Version': {
                    }
                },
                'POP3': {
                    'AuthenticationType': {
                    },
                    'POP3UseProxyMode': {
                    },
                    'PadCommandWhitespace': {
                    },
                    'Password': {
                    },
                    'Username': {
                    }
                },
                'RTF': {
                    'ASCII_Escaping': {
                    },
                    'FictitiousCW': {
                    },
                    'MixedCase': {
                    },
                    'WhiteSpace': {
                    }
                },
                'SELF': {
                    'AREA-ID': {
                    },
                    'AS-ID': {
                    },
                    'AppSimAppProfile': {
                    },
                    'AppSimSmartflow': {
                    },
                    'AppSimSuperflow': {
                    },
                    'AppSimUseNewTuple': {
                    },
                    'ApplicationPings': {
                    },
                    'DelaySeconds': {
                    },
                    'EndingFuzzerOffset': {
                    },
                    'FileTransferExtension': {
                    },
                    'FileTransferFile': {
                    },
                    'FileTransferName': {
                    },
                    'FileTransferRandCase': {
                    },
                    'HTMLPadding': {
                    },
                    'MaximumIterations': {
                    },
                    'MaximumRuntime': {
                    },
                    'Password': {
                    },
                    'ROUTER-ID': {
                    },
                    'Repetitions': {
                    },
                    'ReportCLSIDs': {
                    },
                    'StartingFuzzerOffset': {
                    },
                    'TraversalRequestFilename': {
                    },
                    'TraversalVirtualDirectory': {
                    },
                    'TraversalWindowsDirectory': {
                    },
                    'URI': {
                    },
                    'UnicodeTraversalVirtualDirectory': {
                    },
                    'UnicodeTraversalWindowsDirectory': {
                    },
                    'Username': {
                    }
                },
                'SHELLCODE': {
                    'RandomNops': {
                    }
                },
                'SIP': {
                    'CompactHeaders': {
                    },
                    'EnvelopeType': {
                    },
                    'From': {
                    },
                    'PadHeadersLineBreak': {
                    },
                    'PadHeadersWhitespace': {
                    },
                    'RandomizeCase': {
                    },
                    'ShuffleHeaders': {
                    },
                    'To': {
                    }
                },
                'SMB': {
                    'AuthenticationType': {
                    },
                    'MaxReadSize': {
                    },
                    'MaxWriteSize': {
                    },
                    'Password': {
                    },
                    'RandomPipeOffset': {
                    },
                    'Username': {
                    }
                },
                'SMTP': {
                    'PadCommandWhitespace': {
                    },
                    'SMTPUseProxyMode': {
                    },
                    'ShuffleHeaders': {
                    }
                },
                'SNMP': {
                    'CommunityString': {
                    }
                },
                'SSL': {
                    'Cipher': {
                    },
                    'ClientCertificateFile': {
                    },
                    'ClientKeyFile': {
                    },
                    'DestPortOverride': {
                    },
                    'DisableDefaultStrikeSSL': {
                    },
                    'EnableOnAllHTTP': {
                    },
                    'EnableOnAllTCP': {
                    },
                    'SecurityProtocol': {
                    },
                    'ServerCertificateFile': {
                    },
                    'ServerKeyFile': {
                    }
                },
                'SUNRPC': {
                    'NullCredentialPadding': {
                    },
                    'OneFragmentMultipleTCPSegmentsCount': {
                    },
                    'RPCFragmentTCPSegmentDistribution': {
                    },
                    'TCPFragmentSize': {
                    }
                },
                'TCP': {
                    'AcknowledgeAllSegments': {
                    },
                    'DestinationPort': {
                    },
                    'DestinationPortType': {
                    },
                    'DuplicateBadChecksum': {
                    },
                    'DuplicateBadReset': {
                    },
                    'DuplicateBadSeq': {
                    },
                    'DuplicateBadSyn': {
                    },
                    'DuplicateLastSegment': {
                    },
                    'DuplicateNullFlags': {
                    },
                    'MaxSegmentSize': {
                    },
                    'SegmentOrder': {
                    },
                    'SkipHandshake': {
                    },
                    'SneakAckHandshake': {
                    },
                    'SourcePort': {
                    },
                    'SourcePortType': {
                    }
                },
                'UDP': {
                    'DestinationPort': {
                    },
                    'DestinationPortType': {
                    },
                    'SourcePort': {
                    },
                    'SourcePortType': {
                    }
                },
                'UNIX': {
                    'PadCommandWhitespace': {
                    },
                    'PadPathSlashes': {
                    }
                },
                'Variations': {
                    'Limit': {
                    },
                    'Shuffle': {
                    },
                    'Subset': {
                    },
                    'TestType': {
                    },
                    'VariantTesting': {
                    }
                },
                'operations': {
                    'getStrikeOptions': [{
                        'description': {
                        },
                        'label': {
                        },
                        'name': {
                        },
                        'realtimeGroup': {
                        },
                        'units': {
                        }
                    }]
                }
            },
            'author': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'operations': {
                'delete': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'revision': {
            }
        },
        'loadProfile': {
            'author': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'operations': {
                'createNewCustom': [{
                }],
                'delete': [{
                }],
                'load': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'phase': [{
                'duration': {
                },
                'phaseId': {
                },
                'rampDist.steadyBehavior': {
                },
                'rateDist.min': {
                },
                'rateDist.scope': {
                },
                'rateDist.type': {
                },
                'rateDist.unit': {
                },
                'sessions.max': {
                },
                'sessions.maxPerSecond': {
                },
                'type': {
                }
            }],
            'presets': [{
                'author': {
                },
                'clazz': {
                },
                'createdBy': {
                },
                'createdOn': {
                },
                'description': {
                },
                'label': {
                },
                'lockedBy': {
                },
                'name': {
                },
                'phase': [{
                    'duration': {
                    },
                    'phaseId': {
                    },
                    'rampDist.steadyBehavior': {
                    },
                    'rateDist.min': {
                    },
                    'rateDist.scope': {
                    },
                    'rateDist.type': {
                    },
                    'rateDist.unit': {
                    },
                    'sessions.max': {
                    },
                    'sessions.maxPerSecond': {
                    },
                    'type': {
                    }
                }],
                'regen': {
                },
                'revision': {
                },
                'summaryData': {
                    'activeFlowsSum': {
                    },
                    'appStat': [{
                    }],
                    'basisOfRegeneration': {
                    },
                    'deviceType': {
                    },
                    'downloadBytesSum': {
                    },
                    'dynamicAppNames': {
                    },
                    'dynamicSuperflowName': {
                    },
                    'endTime': {
                    },
                    'magicNumber': {
                    },
                    'miniSlotDuration': {
                    },
                    'phaseDuration': {
                    },
                    'startTime': {
                    },
                    'summaryName': {
                    },
                    'unknownSslAppNames': {
                    },
                    'unknownSslSuperflowName': {
                    },
                    'unknownTcpAppNames': {
                    },
                    'unknownUdpAppNames': {
                    },
                    'uploadBytesSum': {
                    },
                    'version': {
                    }
                }
            }],
            'regen': {
            },
            'revision': {
            },
            'summaryData': {
                'activeFlowsSum': {
                },
                'appStat': [{
                }],
                'basisOfRegeneration': {
                },
                'deviceType': {
                },
                'downloadBytesSum': {
                },
                'dynamicAppNames': {
                },
                'dynamicSuperflowName': {
                },
                'endTime': {
                },
                'magicNumber': {
                },
                'miniSlotDuration': {
                },
                'phaseDuration': {
                },
                'startTime': {
                },
                'summaryName': {
                },
                'unknownSslAppNames': {
                },
                'unknownSslSuperflowName': {
                },
                'unknownTcpAppNames': {
                },
                'unknownUdpAppNames': {
                },
                'uploadBytesSum': {
                },
                'version': {
                }
            }
        },
        'network': {
            'author': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'interfaceCount': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'modelDefinition': {
            },
            'name': {
            },
            'networkModel': {
                'dhcpv6c_cfg': [{
                    'dhcp6c_duid_type': {
                    },
                    'dhcp6c_ia_t1': {
                    },
                    'dhcp6c_ia_t2': {
                    },
                    'dhcp6c_ia_type': {
                    },
                    'dhcp6c_initial_srate': {
                    },
                    'dhcp6c_max_outstanding': {
                    },
                    'dhcp6c_renew_timer': {
                    },
                    'dhcp6c_req_opts_config': {
                    },
                    'dhcp6c_tout_and_retr_config': {
                    },
                    'id': {
                    }
                }],
                'dhcpv6c_req_opts_cfg': [{
                    'dhcpv6v_req_dns_list': {
                    },
                    'dhcpv6v_req_dns_resolvers': {
                    },
                    'dhcpv6v_req_preference': {
                    },
                    'dhcpv6v_req_server_id': {
                    },
                    'id': {
                    }
                }],
                'dhcpv6c_tout_and_retr_cfg': [{
                    'dhcp6c_inforeq_attempts': {
                    },
                    'dhcp6c_initial_inforeq_tout': {
                    },
                    'dhcp6c_initial_rebind_tout': {
                    },
                    'dhcp6c_initial_release_tout': {
                    },
                    'dhcp6c_initial_renew_tout': {
                    },
                    'dhcp6c_initial_req_tout': {
                    },
                    'dhcp6c_initial_sol_tout': {
                    },
                    'dhcp6c_max_inforeq_tout': {
                    },
                    'dhcp6c_max_rebind_tout': {
                    },
                    'dhcp6c_max_renew_tout': {
                    },
                    'dhcp6c_max_req_tout': {
                    },
                    'dhcp6c_max_sol_tout': {
                    },
                    'dhcp6c_release_attempts': {
                    },
                    'dhcp6c_req_attempts': {
                    },
                    'dhcp6c_sol_attempts': {
                    },
                    'id': {
                    }
                }],
                'ds_lite_aftr': [{
                    'b4_count': {
                    },
                    'b4_ip_address': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'prefix_length': {
                    }
                }],
                'ds_lite_b4': [{
                    'aftr_addr': {
                    },
                    'aftr_count': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'host_ip_addr_alloc_mode': {
                    },
                    'host_ip_base_addr': {
                    },
                    'hosts_ip_increment': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'prefix_length': {
                    }
                }],
                'enodeb': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enodebs': [{
                        'enodebCount': {
                        },
                        'ip_address': {
                        },
                        'mme_ip_address': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'netmask': {
                    },
                    'plmn': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'sctp_over_udp': {
                    },
                    'sctp_sport': {
                    }
                }],
                'enodeb6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enodebs': [{
                        'enodebCount': {
                        },
                        'ip_address': {
                        },
                        'mme_ip_address': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    },
                    'sctp_over_udp': {
                    },
                    'sctp_sport': {
                    }
                }],
                'enodeb_mme': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enodebs': [{
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'gateway_ip_address': {
                        },
                        'ip_address': {
                        },
                        'netmask': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'netmask': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'sgw_ip_address': {
                    },
                    'ue_address': {
                    }
                }],
                'enodeb_mme6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enodebs': [{
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'gateway_ip_address': {
                        },
                        'ip_address': {
                        },
                        'prefix_length': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    },
                    'sgw_ip_address': {
                    },
                    'ue_address': {
                    }
                }],
                'enodeb_mme_sgw': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'netmask': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'ue_address': {
                    }
                }],
                'enodeb_mme_sgw6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    },
                    'ue_address': {
                    }
                }],
                'geneve_tep': [{
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'header_options': [{
                        'geneve_data': {
                        },
                        'geneve_option_class': {
                        },
                        'geneve_type': {
                        }
                    }],
                    'id': {
                    },
                    'ip_address': {
                    },
                    'netmask': {
                    },
                    'vni_base': {
                    },
                    'vni_count': {
                    }
                }],
                'ggsn': [{
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'netmask': {
                    }
                }],
                'ggsn6': [{
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'prefix_length': {
                    }
                }],
                'global_config': [{
                    'gtp': {
                    },
                    'id': {
                    }
                }],
                'interface': [{
                    'description': {
                    },
                    'duplicate_mac_address': {
                    },
                    'id': {
                    },
                    'ignore_pause_frames': {
                    },
                    'impairments': {
                        'corrupt_chksum': {
                        },
                        'corrupt_gt256': {
                        },
                        'corrupt_lt256': {
                        },
                        'corrupt_lt64': {
                        },
                        'corrupt_rand': {
                        },
                        'drop': {
                        },
                        'frack': {
                        },
                        'rate': {
                        }
                    },
                    'mac_address': {
                    },
                    'mtu': {
                    },
                    'number': {
                    },
                    'packet_filter': {
                        'dest_ip': {
                        },
                        'dest_port': {
                        },
                        'filter': {
                        },
                        'not_dest_ip': {
                        },
                        'not_dest_port': {
                        },
                        'not_src_ip': {
                        },
                        'not_src_port': {
                        },
                        'not_vlan': {
                        },
                        'src_ip': {
                        },
                        'src_port': {
                        },
                        'vlan': {
                        }
                    },
                    'use_vnic_mac_address': {
                    },
                    'vlan_key': {
                    }
                }],
                'ip6_dhcp_server': [{
                    'default_container': {
                    },
                    'default_lease_time': {
                    },
                    'gateway_ip_address': {
                    },
                    'ia_type': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'max_lease_time': {
                    },
                    'offer_lifetime': {
                    },
                    'pool_base_address': {
                    },
                    'pool_dns_address1': {
                    },
                    'pool_dns_address2': {
                    },
                    'pool_prefix_length': {
                    },
                    'pool_size': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip6_dns_config': [{
                    'dns_domain': {
                    },
                    'dns_server_address': {
                    },
                    'id': {
                    }
                }],
                'ip6_dns_proxy': [{
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    },
                    'id': {
                    }
                }],
                'ip6_external_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    }
                }],
                'ip6_geneve_tep': [{
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'header_options': [{
                        'geneve_data': {
                        },
                        'geneve_option_class': {
                        },
                        'geneve_type': {
                        }
                    }],
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    },
                    'vni_base': {
                    },
                    'vni_count': {
                    }
                }],
                'ip6_mac_static_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'mac_address': {
                    },
                    'mtu': {
                    },
                    'prefix_length': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    },
                    'tep_vni_mapping': {
                    }
                }],
                'ip6_router': [{
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'hosts_ip_alloc_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip6_static_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'dns_proxy': {
                    },
                    'enable_stats': {
                    },
                    'gateway_ip_address': {
                    },
                    'host_ipv6_addr_alloc_mode': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ip_alloc_container': {
                    },
                    'ip_selection_type': {
                    },
                    'maxmbps_per_host': {
                    },
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'prefix_length': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    }
                }],
                'ip_dhcp_hosts': [{
                    'accept_local_offers_only': {
                    },
                    'allocation_rate': {
                    },
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns_proxy': {
                    },
                    'enable_stats': {
                    },
                    'id': {
                    },
                    'ldap': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    }
                }],
                'ip_dhcp_server': [{
                    'accept_local_requests_only': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_time': {
                    },
                    'netmask': {
                    }
                }],
                'ip_dns_config': [{
                    'dns_domain': {
                    },
                    'dns_server_address': {
                    },
                    'id': {
                    }
                }],
                'ip_dns_proxy': [{
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    },
                    'id': {
                    }
                }],
                'ip_external_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    }
                }],
                'ip_ldap_server': [{
                    'auth_timeout': {
                    },
                    'authentication_rate': {
                    },
                    'dn_fixed_val': {
                    },
                    'id': {
                    },
                    'ldap_password_start_tag': {
                    },
                    'ldap_server_address': {
                    },
                    'ldap_user_count': {
                    },
                    'ldap_user_max': {
                    },
                    'ldap_user_min': {
                    },
                    'ldap_username_start_tag': {
                    }
                }],
                'ip_mac_static_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'mac_address': {
                    },
                    'mtu': {
                    },
                    'netmask': {
                    },
                    'proxy': {
                    },
                    'tags': {
                    },
                    'tep_vni_mapping': {
                    }
                }],
                'ip_router': [{
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'ip_static_hosts': [{
                    'behind_snapt': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'dns_proxy': {
                    },
                    'enable_stats': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ip_selection_type': {
                    },
                    'ldap': {
                    },
                    'maxmbps_per_host': {
                    },
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'netmask': {
                    },
                    'proxy': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'tags': {
                    }
                }],
                'ipsec_config': [{
                    'debug_log': {
                    },
                    'dpd_delay': {
                    },
                    'dpd_enabled': {
                    },
                    'dpd_timeout': {
                    },
                    'enable_xauth': {
                    },
                    'esp_auth_alg': {
                    },
                    'esp_encr_alg': {
                    },
                    'id': {
                    },
                    'ike_1to1': {
                    },
                    'ike_auth_alg': {
                    },
                    'ike_dh': {
                    },
                    'ike_encr_alg': {
                    },
                    'ike_lifetime': {
                    },
                    'ike_mode': {
                    },
                    'ike_pfs': {
                    },
                    'ike_prf_alg': {
                    },
                    'ike_version': {
                    },
                    'init_rate': {
                    },
                    'initial_contact': {
                    },
                    'ipsec_lifetime': {
                    },
                    'left_id': {
                    },
                    'max_outstanding': {
                    },
                    'nat_traversal': {
                    },
                    'psk': {
                    },
                    'rekey_margin': {
                    },
                    'retrans_interval': {
                    },
                    'right_id': {
                    },
                    'setup_timeout': {
                    },
                    'wildcard_tsr': {
                    },
                    'xauth_password': {
                    },
                    'xauth_username': {
                    }
                }],
                'ipsec_router': [{
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ike_peer_ip_address': {
                    },
                    'ip_address': {
                    },
                    'ipsec': {
                    },
                    'netmask': {
                    }
                }],
                'mme_sgw_pgw': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'netmask': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'ue_info': {
                    }
                }],
                'mme_sgw_pgw6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'ue_info': {
                    }
                }],
                'mobility_session_info': [{
                    'access_point_name': {
                    },
                    'bearers': [{
                        'qci_label': {
                        }
                    }],
                    'id': {
                    },
                    'initiated_dedicated_bearers': {
                    },
                    'password': {
                    },
                    'username': {
                    }
                }],
                'mpls_settings': [{
                    'id': {
                    },
                    'mpls_tags': [{
                        'mpls_exp': {
                        },
                        'mpls_label': {
                        },
                        'mpls_ttl': {
                        }
                    }]
                }],
                'path_advanced': [{
                    'destination_container': {
                    },
                    'destination_port_algorithm': {
                    },
                    'destination_port_base': {
                    },
                    'destination_port_count': {
                    },
                    'enable_external_file': {
                    },
                    'file': {
                    },
                    'id': {
                    },
                    'source_container': {
                    },
                    'source_port_algorithm': {
                    },
                    'source_port_base': {
                    },
                    'source_port_count': {
                    },
                    'stream_group': {
                    },
                    'tags': {
                    },
                    'tuple_limit': {
                    },
                    'xor_bits': {
                    }
                }],
                'path_basic': [{
                    'destination_container': {
                    },
                    'id': {
                    },
                    'source_container': {
                    }
                }],
                'pgw': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'netmask': {
                    },
                    'plmn': {
                    }
                }],
                'pgw6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    }
                }],
                'plmn': [{
                    'description': {
                    },
                    'id': {
                    },
                    'mcc': {
                    },
                    'mnc': {
                    }
                }],
                'sgsn': [{
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'sgsn6': [{
                    'default_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    }
                }],
                'sgw_pgw': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'netmask': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'sgw_advertised_sgw': {
                    }
                }],
                'sgw_pgw6': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'gateway_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'lease_address_v6': {
                    },
                    'max_sessions': {
                    },
                    'plmn': {
                    },
                    'prefix_length': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'sgw_advertised_sgw': {
                    }
                }],
                'sixrd_ce': [{
                    'br_ip_address': {
                    },
                    'count': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enable_stats': {
                    },
                    'gateway_ip_address': {
                    },
                    'hosts_per_ce': {
                    },
                    'id': {
                    },
                    'ip4_mask_length': {
                    },
                    'ip_address': {
                    },
                    'netmask': {
                    },
                    'sixrd_prefix': {
                    },
                    'sixrd_prefix_length': {
                    },
                    'tags': {
                    }
                }],
                'slaac_cfg': [{
                    'enable_dad': {
                    },
                    'fallback_ip_address': {
                    },
                    'id': {
                    },
                    'stateless_dhcpv6c_cfg': {
                    },
                    'use_rand_addr': {
                    }
                }],
                'ue': [{
                    'allocation_rate': {
                    },
                    'behind_snapt': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'enable_stats': {
                    },
                    'id': {
                    },
                    'mobility_action': {
                    },
                    'mobility_interval_ms': {
                    },
                    'mobility_with_traffic': {
                    },
                    'proxy': {
                    },
                    'request_ipv6': {
                    },
                    'tags': {
                    },
                    'ue_info': {
                    }
                }],
                'ue_info': [{
                    'count': {
                    },
                    'id': {
                    },
                    'imei_base': {
                    },
                    'imsi_base': {
                    },
                    'maxmbps_per_ue': {
                    },
                    'mobility_session_infos': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'msisdn_base': {
                    },
                    'operator_variant': {
                    },
                    'secret_key': {
                    },
                    'secret_key_step': {
                    }
                }],
                'vlan': [{
                    'count': {
                    },
                    'default_container': {
                    },
                    'description': {
                    },
                    'duplicate_mac_address': {
                    },
                    'id': {
                    },
                    'inner_vlan': {
                    },
                    'mac_address': {
                    },
                    'mtu': {
                    },
                    'outer_vlan': {
                    },
                    'tpid': {
                    }
                }]
            },
            'operations': {
                'addOpenRecent': [{
                }],
                'delete': [{
                }],
                'exportCSV': [{
                }],
                'exportNetwork': [{
                }],
                'getRecent': [{
                }],
                'importNetwork': [{
                }],
                'list': [{
                }],
                'load': [{
                }],
                'networkInfo': [{
                    'author': {
                    },
                    'clazz': {
                    },
                    'createdBy': {
                    },
                    'createdOn': {
                    },
                    'description': {
                    },
                    'interfaceCount': {
                    },
                    'label': {
                    },
                    'lockedBy': {
                    },
                    'name': {
                    },
                    'networkModel': {
                        'dhcpv6c_cfg': [{
                            'dhcp6c_duid_type': {
                            },
                            'dhcp6c_ia_t1': {
                            },
                            'dhcp6c_ia_t2': {
                            },
                            'dhcp6c_ia_type': {
                            },
                            'dhcp6c_initial_srate': {
                            },
                            'dhcp6c_max_outstanding': {
                            },
                            'dhcp6c_renew_timer': {
                            },
                            'dhcp6c_req_opts_config': {
                            },
                            'dhcp6c_tout_and_retr_config': {
                            },
                            'id': {
                            }
                        }],
                        'dhcpv6c_req_opts_cfg': [{
                            'dhcpv6v_req_dns_list': {
                            },
                            'dhcpv6v_req_dns_resolvers': {
                            },
                            'dhcpv6v_req_preference': {
                            },
                            'dhcpv6v_req_server_id': {
                            },
                            'id': {
                            }
                        }],
                        'dhcpv6c_tout_and_retr_cfg': [{
                            'dhcp6c_inforeq_attempts': {
                            },
                            'dhcp6c_initial_inforeq_tout': {
                            },
                            'dhcp6c_initial_rebind_tout': {
                            },
                            'dhcp6c_initial_release_tout': {
                            },
                            'dhcp6c_initial_renew_tout': {
                            },
                            'dhcp6c_initial_req_tout': {
                            },
                            'dhcp6c_initial_sol_tout': {
                            },
                            'dhcp6c_max_inforeq_tout': {
                            },
                            'dhcp6c_max_rebind_tout': {
                            },
                            'dhcp6c_max_renew_tout': {
                            },
                            'dhcp6c_max_req_tout': {
                            },
                            'dhcp6c_max_sol_tout': {
                            },
                            'dhcp6c_release_attempts': {
                            },
                            'dhcp6c_req_attempts': {
                            },
                            'dhcp6c_sol_attempts': {
                            },
                            'id': {
                            }
                        }],
                        'ds_lite_aftr': [{
                            'b4_count': {
                            },
                            'b4_ip_address': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'ipv6_addr_alloc_mode': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'ds_lite_b4': [{
                            'aftr_addr': {
                            },
                            'aftr_count': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'host_ip_addr_alloc_mode': {
                            },
                            'host_ip_base_addr': {
                            },
                            'hosts_ip_increment': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'ipv6_addr_alloc_mode': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'enodeb': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enodebs': [{
                                'enodebCount': {
                                },
                                'ip_address': {
                                },
                                'mme_ip_address': {
                                }
                            }],
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'netmask': {
                            },
                            'plmn': {
                            },
                            'psn': {
                            },
                            'psn_netmask': {
                            },
                            'sctp_over_udp': {
                            },
                            'sctp_sport': {
                            }
                        }],
                        'enodeb6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enodebs': [{
                                'enodebCount': {
                                },
                                'ip_address': {
                                },
                                'mme_ip_address': {
                                }
                            }],
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            },
                            'sctp_over_udp': {
                            },
                            'sctp_sport': {
                            }
                        }],
                        'enodeb_mme': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enodebs': [{
                                'default_container': {
                                },
                                'enodebCount': {
                                },
                                'gateway_ip_address': {
                                },
                                'ip_address': {
                                },
                                'netmask': {
                                }
                            }],
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_allocation_mode': {
                            },
                            'mme_ip_address': {
                            },
                            'netmask': {
                            },
                            'pgw_ip_address': {
                            },
                            'plmn': {
                            },
                            'sgw_ip_address': {
                            },
                            'ue_address': {
                            }
                        }],
                        'enodeb_mme6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enodebs': [{
                                'default_container': {
                                },
                                'enodebCount': {
                                },
                                'gateway_ip_address': {
                                },
                                'ip_address': {
                                },
                                'prefix_length': {
                                }
                            }],
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_allocation_mode': {
                            },
                            'mme_ip_address': {
                            },
                            'pgw_ip_address': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            },
                            'sgw_ip_address': {
                            },
                            'ue_address': {
                            }
                        }],
                        'enodeb_mme_sgw': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_allocation_mode': {
                            },
                            'mme_ip_address': {
                            },
                            'netmask': {
                            },
                            'pgw_ip_address': {
                            },
                            'plmn': {
                            },
                            'ue_address': {
                            }
                        }],
                        'enodeb_mme_sgw6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_allocation_mode': {
                            },
                            'mme_ip_address': {
                            },
                            'pgw_ip_address': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            },
                            'ue_address': {
                            }
                        }],
                        'geneve_tep': [{
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'header_options': [{
                                'geneve_data': {
                                },
                                'geneve_option_class': {
                                },
                                'geneve_type': {
                                }
                            }],
                            'id': {
                            },
                            'ip_address': {
                            },
                            'netmask': {
                            },
                            'vni_base': {
                            },
                            'vni_count': {
                            }
                        }],
                        'ggsn': [{
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'ggsn_advertised_control_ip_address': {
                            },
                            'ggsn_advertised_data_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'netmask': {
                            }
                        }],
                        'ggsn6': [{
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'ggsn_advertised_control_ip_address': {
                            },
                            'ggsn_advertised_data_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'global_config': [{
                            'gtp': {
                            },
                            'id': {
                            }
                        }],
                        'interface': [{
                            'description': {
                            },
                            'duplicate_mac_address': {
                            },
                            'id': {
                            },
                            'ignore_pause_frames': {
                            },
                            'impairments': {
                                'corrupt_chksum': {
                                },
                                'corrupt_gt256': {
                                },
                                'corrupt_lt256': {
                                },
                                'corrupt_lt64': {
                                },
                                'corrupt_rand': {
                                },
                                'drop': {
                                },
                                'frack': {
                                },
                                'rate': {
                                }
                            },
                            'mac_address': {
                            },
                            'mtu': {
                            },
                            'number': {
                            },
                            'packet_filter': {
                                'dest_ip': {
                                },
                                'dest_port': {
                                },
                                'filter': {
                                },
                                'not_dest_ip': {
                                },
                                'not_dest_port': {
                                },
                                'not_src_ip': {
                                },
                                'not_src_port': {
                                },
                                'not_vlan': {
                                },
                                'src_ip': {
                                },
                                'src_port': {
                                },
                                'vlan': {
                                }
                            },
                            'use_vnic_mac_address': {
                            },
                            'vlan_key': {
                            }
                        }],
                        'ip6_dhcp_server': [{
                            'default_container': {
                            },
                            'default_lease_time': {
                            },
                            'gateway_ip_address': {
                            },
                            'ia_type': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'max_lease_time': {
                            },
                            'offer_lifetime': {
                            },
                            'pool_base_address': {
                            },
                            'pool_dns_address1': {
                            },
                            'pool_dns_address2': {
                            },
                            'pool_prefix_length': {
                            },
                            'pool_size': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'ip6_dns_config': [{
                            'dns_domain': {
                            },
                            'dns_server_address': {
                            },
                            'id': {
                            }
                        }],
                        'ip6_dns_proxy': [{
                            'dns_proxy_ip_base': {
                            },
                            'dns_proxy_ip_count': {
                            },
                            'dns_proxy_src_ip_base': {
                            },
                            'dns_proxy_src_ip_count': {
                            },
                            'id': {
                            }
                        }],
                        'ip6_external_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            }
                        }],
                        'ip6_geneve_tep': [{
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'header_options': [{
                                'geneve_data': {
                                },
                                'geneve_option_class': {
                                },
                                'geneve_type': {
                                }
                            }],
                            'id': {
                            },
                            'ip_address': {
                            },
                            'prefix_length': {
                            },
                            'vni_base': {
                            },
                            'vni_count': {
                            }
                        }],
                        'ip6_mac_static_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'mac_address': {
                            },
                            'mtu': {
                            },
                            'prefix_length': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            },
                            'tep_vni_mapping': {
                            }
                        }],
                        'ip6_router': [{
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'hosts_ip_alloc_container': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'ip6_static_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'dns_proxy': {
                            },
                            'enable_stats': {
                            },
                            'gateway_ip_address': {
                            },
                            'host_ipv6_addr_alloc_mode': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'ip_alloc_container': {
                            },
                            'ip_selection_type': {
                            },
                            'maxmbps_per_host': {
                            },
                            'mpls_list': [{
                                'id': {
                                },
                                'value': {
                                }
                            }],
                            'prefix_length': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            }
                        }],
                        'ip_dhcp_hosts': [{
                            'accept_local_offers_only': {
                            },
                            'allocation_rate': {
                            },
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns_proxy': {
                            },
                            'enable_stats': {
                            },
                            'id': {
                            },
                            'ldap': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            }
                        }],
                        'ip_dhcp_server': [{
                            'accept_local_requests_only': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_time': {
                            },
                            'netmask': {
                            }
                        }],
                        'ip_dns_config': [{
                            'dns_domain': {
                            },
                            'dns_server_address': {
                            },
                            'id': {
                            }
                        }],
                        'ip_dns_proxy': [{
                            'dns_proxy_ip_base': {
                            },
                            'dns_proxy_ip_count': {
                            },
                            'dns_proxy_src_ip_base': {
                            },
                            'dns_proxy_src_ip_count': {
                            },
                            'id': {
                            }
                        }],
                        'ip_external_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            }
                        }],
                        'ip_ldap_server': [{
                            'auth_timeout': {
                            },
                            'authentication_rate': {
                            },
                            'dn_fixed_val': {
                            },
                            'id': {
                            },
                            'ldap_password_start_tag': {
                            },
                            'ldap_server_address': {
                            },
                            'ldap_user_count': {
                            },
                            'ldap_user_max': {
                            },
                            'ldap_user_min': {
                            },
                            'ldap_username_start_tag': {
                            }
                        }],
                        'ip_mac_static_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'mac_address': {
                            },
                            'mtu': {
                            },
                            'netmask': {
                            },
                            'proxy': {
                            },
                            'tags': {
                            },
                            'tep_vni_mapping': {
                            }
                        }],
                        'ip_router': [{
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'netmask': {
                            }
                        }],
                        'ip_static_hosts': [{
                            'behind_snapt': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'dns_proxy': {
                            },
                            'enable_stats': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'ip_selection_type': {
                            },
                            'ldap': {
                            },
                            'maxmbps_per_host': {
                            },
                            'mpls_list': [{
                                'id': {
                                },
                                'value': {
                                }
                            }],
                            'netmask': {
                            },
                            'proxy': {
                            },
                            'psn': {
                            },
                            'psn_netmask': {
                            },
                            'tags': {
                            }
                        }],
                        'ipsec_config': [{
                            'debug_log': {
                            },
                            'dpd_delay': {
                            },
                            'dpd_enabled': {
                            },
                            'dpd_timeout': {
                            },
                            'enable_xauth': {
                            },
                            'esp_auth_alg': {
                            },
                            'esp_encr_alg': {
                            },
                            'id': {
                            },
                            'ike_1to1': {
                            },
                            'ike_auth_alg': {
                            },
                            'ike_dh': {
                            },
                            'ike_encr_alg': {
                            },
                            'ike_lifetime': {
                            },
                            'ike_mode': {
                            },
                            'ike_pfs': {
                            },
                            'ike_prf_alg': {
                            },
                            'ike_version': {
                            },
                            'init_rate': {
                            },
                            'initial_contact': {
                            },
                            'ipsec_lifetime': {
                            },
                            'left_id': {
                            },
                            'max_outstanding': {
                            },
                            'nat_traversal': {
                            },
                            'psk': {
                            },
                            'rekey_margin': {
                            },
                            'retrans_interval': {
                            },
                            'right_id': {
                            },
                            'setup_timeout': {
                            },
                            'wildcard_tsr': {
                            },
                            'xauth_password': {
                            },
                            'xauth_username': {
                            }
                        }],
                        'ipsec_router': [{
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ike_peer_ip_address': {
                            },
                            'ip_address': {
                            },
                            'ipsec': {
                            },
                            'netmask': {
                            }
                        }],
                        'mme_sgw_pgw': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'netmask': {
                            },
                            'plmn': {
                            },
                            'sgw_advertised_pgw': {
                            },
                            'sgw_advertised_sgw': {
                            },
                            'ue_info': {
                            }
                        }],
                        'mme_sgw_pgw6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            },
                            'sgw_advertised_pgw': {
                            },
                            'sgw_advertised_sgw': {
                            },
                            'ue_info': {
                            }
                        }],
                        'mobility_session_info': [{
                            'access_point_name': {
                            },
                            'bearers': [{
                                'qci_label': {
                                }
                            }],
                            'id': {
                            },
                            'initiated_dedicated_bearers': {
                            },
                            'password': {
                            },
                            'username': {
                            }
                        }],
                        'mpls_settings': [{
                            'id': {
                            },
                            'mpls_tags': [{
                                'mpls_exp': {
                                },
                                'mpls_label': {
                                },
                                'mpls_ttl': {
                                }
                            }]
                        }],
                        'path_advanced': [{
                            'destination_container': {
                            },
                            'destination_port_algorithm': {
                            },
                            'destination_port_base': {
                            },
                            'destination_port_count': {
                            },
                            'enable_external_file': {
                            },
                            'file': {
                            },
                            'id': {
                            },
                            'source_container': {
                            },
                            'source_port_algorithm': {
                            },
                            'source_port_base': {
                            },
                            'source_port_count': {
                            },
                            'stream_group': {
                            },
                            'tags': {
                            },
                            'tuple_limit': {
                            },
                            'xor_bits': {
                            }
                        }],
                        'path_basic': [{
                            'destination_container': {
                            },
                            'id': {
                            },
                            'source_container': {
                            }
                        }],
                        'pgw': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'netmask': {
                            },
                            'plmn': {
                            }
                        }],
                        'pgw6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'plmn': [{
                            'description': {
                            },
                            'id': {
                            },
                            'mcc': {
                            },
                            'mnc': {
                            }
                        }],
                        'sgsn': [{
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'ggsn_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'netmask': {
                            }
                        }],
                        'sgsn6': [{
                            'default_container': {
                            },
                            'gateway_ip_address': {
                            },
                            'ggsn_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'prefix_length': {
                            }
                        }],
                        'sgw_pgw': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'netmask': {
                            },
                            'plmn': {
                            },
                            'sgw_advertised_pgw': {
                            },
                            'sgw_advertised_sgw': {
                            }
                        }],
                        'sgw_pgw6': [{
                            'default_container': {
                            },
                            'dns': {
                            },
                            'gateway_ip_address': {
                            },
                            'id': {
                            },
                            'ip_address': {
                            },
                            'lease_address': {
                            },
                            'lease_address_v6': {
                            },
                            'max_sessions': {
                            },
                            'plmn': {
                            },
                            'prefix_length': {
                            },
                            'sgw_advertised_pgw': {
                            },
                            'sgw_advertised_sgw': {
                            }
                        }],
                        'sixrd_ce': [{
                            'br_ip_address': {
                            },
                            'count': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enable_stats': {
                            },
                            'gateway_ip_address': {
                            },
                            'hosts_per_ce': {
                            },
                            'id': {
                            },
                            'ip4_mask_length': {
                            },
                            'ip_address': {
                            },
                            'netmask': {
                            },
                            'sixrd_prefix': {
                            },
                            'sixrd_prefix_length': {
                            },
                            'tags': {
                            }
                        }],
                        'slaac_cfg': [{
                            'enable_dad': {
                            },
                            'fallback_ip_address': {
                            },
                            'id': {
                            },
                            'stateless_dhcpv6c_cfg': {
                            },
                            'use_rand_addr': {
                            }
                        }],
                        'ue': [{
                            'allocation_rate': {
                            },
                            'behind_snapt': {
                            },
                            'default_container': {
                            },
                            'dns': {
                            },
                            'enable_stats': {
                            },
                            'id': {
                            },
                            'mobility_action': {
                            },
                            'mobility_interval_ms': {
                            },
                            'mobility_with_traffic': {
                            },
                            'proxy': {
                            },
                            'request_ipv6': {
                            },
                            'tags': {
                            },
                            'ue_info': {
                            }
                        }],
                        'ue_info': [{
                            'count': {
                            },
                            'id': {
                            },
                            'imei_base': {
                            },
                            'imsi_base': {
                            },
                            'maxmbps_per_ue': {
                            },
                            'mobility_session_infos': [{
                                'id': {
                                },
                                'value': {
                                }
                            }],
                            'msisdn_base': {
                            },
                            'operator_variant': {
                            },
                            'secret_key': {
                            },
                            'secret_key_step': {
                            }
                        }],
                        'vlan': [{
                            'count': {
                            },
                            'default_container': {
                            },
                            'description': {
                            },
                            'duplicate_mac_address': {
                            },
                            'id': {
                            },
                            'inner_vlan': {
                            },
                            'mac_address': {
                            },
                            'mtu': {
                            },
                            'outer_vlan': {
                            },
                            'tpid': {
                            }
                        }]
                    },
                    'revision': {
                    }
                }],
                'new': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'revision': {
            }
        },
        'remote': {
            'operations': {
                'connectChassis': [{
                }],
                'disconnectChassis': [{
                }]
            }
        },
        'reports': {
            'duration': {
            },
            'endtime': {
            },
            'isPartOfResiliency': {
            },
            'iteration': {
            },
            'label': {
            },
            'name': {
            },
            'network': {
            },
            'operations': {
                'delete': [{
                }],
                'exportReport': [{
                }],
                'getReportContents': [{
                }],
                'getReportTable': [{
                }],
                'search': [{
                }]
            },
            'result': {
            },
            'size': {
            },
            'starttime': {
            },
            'testid': {
                'host': {
                },
                'iteration': {
                },
                'name': {
                }
            },
            'testname': {
            },
            'user': {
            }
        },
        'results': [{
            'content': {
            },
            'datasetvals': {
            },
            'name': {
            },
            'operations': {
                'getGroups': [{
                    'author': {
                    },
                    'clazz': {
                    },
                    'createdBy': {
                    },
                    'createdOn': {
                    },
                    'description': {
                    },
                    'label': {
                    },
                    'lockedBy': {
                    },
                    'revision': {
                    }
                }],
                'getHistoricalResultSize': [{
                }],
                'getHistoricalSeries': [{
                }]
            }
        }],
        'statistics': {
            'component': [{
                'label': {
                },
                'statNames': [{
                    'description': {
                    },
                    'label': {
                    },
                    'name': {
                    },
                    'realtimeGroup': {
                    },
                    'units': {
                    }
                }]
            }]
        },
        'strikeList': {
            'SecurityBehavior': {
            },
            'StrikeOptions': {
            },
            'author': {
            },
            'clazz': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'numStrikes': {
            },
            'operations': {
                'add': [{
                }],
                'delete': [{
                }],
                'exportStrikeList': [{
                }],
                'importStrikeList': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'remove': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'queryString': {
            },
            'revision': {
            },
            'strikes': [{
                'category': {
                },
                'direction': {
                },
                'fileExtension': {
                },
                'fileSize': {
                },
                'id': {
                },
                'keyword': [{
                    'name': {
                    }
                }],
                'name': {
                },
                'path': {
                },
                'protocol': {
                },
                'reference': [{
                    'label': {
                    },
                    'type': {
                    },
                    'value': {
                    }
                }],
                'severity': {
                },
                'strike': {
                },
                'strikeset': {
                },
                'variants': {
                },
                'year': {
                }
            }]
        },
        'strikes': {
            'category': {
            },
            'direction': {
            },
            'fileExtension': {
            },
            'fileSize': {
            },
            'id': {
            },
            'keyword': [{
                'name': {
                }
            }],
            'name': {
            },
            'operations': {
                'search': [{
                }]
            },
            'path': {
            },
            'protocol': {
            },
            'reference': [{
                'label': {
                },
                'type': {
                },
                'value': {
                }
            }],
            'severity': {
            },
            'variants': {
            },
            'year': {
            }
        },
        'superflow': {
            'actions': [{
                'actionInfo': [{
                    'description': {
                    },
                    'label': {
                    },
                    'name': {
                    },
                    'realtimeGroup': {
                    },
                    'units': {
                    }
                }],
                'exflows': {
                },
                'flowid': {
                },
                'flowlabel': {
                },
                'gotoBlock': {
                },
                'id': {
                },
                'label': {
                },
                'matchBlock': {
                },
                'operations': {
                    'getActionChoices': [{
                    }],
                    'getActionInfo': [{
                        'description': {
                        },
                        'label': {
                        },
                        'name': {
                        },
                        'realtimeGroup': {
                        },
                        'units': {
                        }
                    }]
                },
                'params': {
                },
                'source': {
                },
                'type': {
                }
            }],
            'author': {
            },
            'clazz': {
            },
            'constraints': {
            },
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'estimate_bytes': {
            },
            'estimate_flows': {
            },
            'flows': [{
                'flowcount': {
                },
                'from': {
                },
                'id': {
                },
                'label': {
                },
                'name': {
                },
                'operations': {
                    'getCannedFlows': [{
                    }],
                    'getFlowChoices': [{
                        'author': {
                        },
                        'clazz': {
                        },
                        'createdBy': {
                        },
                        'createdOn': {
                        },
                        'description': {
                        },
                        'label': {
                        },
                        'lockedBy': {
                        },
                        'revision': {
                        }
                    }]
                },
                'params': {
                },
                'singleNP': {
                },
                'to': {
                }
            }],
            'generated': {
            },
            'hosts': [{
                'hostname': {
                },
                'id': {
                },
                'iface': {
                },
                'ip': {
                    'type': {
                    }
                }
            }],
            'label': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'operations': {
                'addAction': [{
                }],
                'addFlow': [{
                }],
                'addHost': [{
                }],
                'delete': [{
                }],
                'importResource': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'removeAction': [{
                }],
                'removeFlow': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }]
            },
            'params': {
            },
            'percentBandwidth': {
            },
            'percentFlows': {
            },
            'revision': {
            },
            'seed': {
            },
            'settings': [{
                'description': {
                },
                'label': {
                },
                'name': {
                },
                'realtimeGroup': {
                },
                'units': {
                }
            }],
            'weight': {
            }
        },
        'testmodel': {
            'author': {
            },
            'clazz': {
            },
            'component': [{
                '@type:appsim': {
                    'app': {
                        'fidelity': {
                        },
                        'removedns': {
                        },
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        }
                    },
                    'delayStart': {
                    },
                    'experimental': {
                        'tcpSegmentsBurst': {
                        },
                        'unify_l4_bufs': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'profile': {
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'resources': {
                        'expand': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'ssl': {
                        'client_record_len': {
                        },
                        'server_record_len': {
                        },
                        'sslReuseType': {
                        },
                        'ssl_client_keylog': {
                        },
                        'ssl_keylog_max_entries': {
                        },
                        'upgrade': {
                        }
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    }
                },
                '@type:clientsim': {
                    'app': {
                        'fidelity': {
                        },
                        'removedns': {
                        },
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        }
                    },
                    'delayStart': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'resources': {
                        'expand': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'ssl': {
                        'client_record_len': {
                        },
                        'server_record_len': {
                        },
                        'sslReuseType': {
                        },
                        'ssl_client_keylog': {
                        },
                        'ssl_keylog_max_entries': {
                        },
                        'upgrade': {
                        }
                    },
                    'superflow': {
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    }
                },
                '@type:layer2': {
                    'advanced': {
                        'ethTypeField': {
                        },
                        'ethTypeVal': {
                        }
                    },
                    'bidirectional': {
                    },
                    'delayStart': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationFrames': {
                        },
                        'durationTime': {
                        }
                    },
                    'maxStreams': {
                    },
                    'payload': {
                        'data': {
                        },
                        'dataWidth': {
                        },
                        'type': {
                        }
                    },
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfLength': {
                        },
                        'udfMode': {
                        },
                        'udfOffset': {
                        }
                    },
                    'rateDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'ramptype': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'mixlen1': {
                        },
                        'mixlen10': {
                        },
                        'mixlen2': {
                        },
                        'mixlen3': {
                        },
                        'mixlen4': {
                        },
                        'mixlen5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen7': {
                        },
                        'mixlen8': {
                        },
                        'mixlen9': {
                        },
                        'mixweight1': {
                        },
                        'mixweight10': {
                        },
                        'mixweight2': {
                        },
                        'mixweight3': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'slowStart': {
                    },
                    'slowStartFps': {
                    }
                },
                '@type:layer3': {
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'addrGenMode': {
                    },
                    'advancedIPv4': {
                        'checksumField': {
                        },
                        'checksumVal': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        },
                        'optionHeaderData': {
                        },
                        'optionHeaderField': {
                        },
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'advancedIPv6': {
                        'extensionHeaderData': {
                        },
                        'extensionHeaderField': {
                        },
                        'flowLabel': {
                        },
                        'hopLimit': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        }
                    },
                    'advancedUDP': {
                        'checksumField': {
                        },
                        'checksumVal': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        }
                    },
                    'bidirectional': {
                    },
                    'delayStart': {
                    },
                    'dstPort': {
                    },
                    'dstPortMask': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationFrames': {
                        },
                        'durationTime': {
                        }
                    },
                    'enableTCP': {
                    },
                    'maxStreams': {
                    },
                    'payload': {
                        'data': {
                        },
                        'dataWidth': {
                        },
                        'type': {
                        }
                    },
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfLength': {
                        },
                        'udfMode': {
                        },
                        'udfOffset': {
                        }
                    },
                    'randomizeIP': {
                    },
                    'rateDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'ramptype': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'mixlen1': {
                        },
                        'mixlen10': {
                        },
                        'mixlen2': {
                        },
                        'mixlen3': {
                        },
                        'mixlen4': {
                        },
                        'mixlen5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen7': {
                        },
                        'mixlen8': {
                        },
                        'mixlen9': {
                        },
                        'mixweight1': {
                        },
                        'mixweight10': {
                        },
                        'mixweight2': {
                        },
                        'mixweight3': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'slowStart': {
                    },
                    'slowStartFps': {
                    },
                    'srcPort': {
                    },
                    'srcPortMask': {
                    },
                    'syncIP': {
                    },
                    'udpDstPortMode': {
                    },
                    'udpSrcPortMode': {
                    }
                },
                '@type:layer3advanced': {
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'advancedIPv4': {
                        'checksumField': {
                        },
                        'checksumVal': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        },
                        'optionHeaderData': {
                        },
                        'optionHeaderField': {
                        },
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'advancedIPv6': {
                        'extensionHeaderData': {
                        },
                        'extensionHeaderField': {
                        },
                        'flowLabel': {
                        },
                        'hopLimit': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        }
                    },
                    'advancedUDP': {
                        'checksumField': {
                        },
                        'checksumVal': {
                        },
                        'lengthField': {
                        },
                        'lengthVal': {
                        }
                    },
                    'bidirectional': {
                    },
                    'delayStart': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationFrames': {
                        },
                        'durationTime': {
                        }
                    },
                    'enablePerStreamStats': {
                    },
                    'enableTCP': {
                    },
                    'payload': {
                        'data': {
                        },
                        'dataWidth': {
                        },
                        'type': {
                        }
                    },
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfLength': {
                        },
                        'udfMode': {
                        },
                        'udfOffset': {
                        }
                    },
                    'rateDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'ramptype': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'mixlen1': {
                        },
                        'mixlen10': {
                        },
                        'mixlen2': {
                        },
                        'mixlen3': {
                        },
                        'mixlen4': {
                        },
                        'mixlen5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen7': {
                        },
                        'mixlen8': {
                        },
                        'mixlen9': {
                        },
                        'mixweight1': {
                        },
                        'mixweight10': {
                        },
                        'mixweight2': {
                        },
                        'mixweight3': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'rate': {
                        },
                        'type': {
                        },
                        'unit': {
                        }
                    },
                    'slowStart': {
                    },
                    'slowStartFps': {
                    },
                    'tuple_gen_seed': {
                    }
                },
                '@type:layer4': {
                    'delayStart': {
                    },
                    'dstPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'packetsPerSession': {
                    },
                    'payload': {
                        'add_timestamp': {
                        },
                        'data': {
                        },
                        'http_type': {
                        },
                        'transport': {
                        },
                        'type': {
                        }
                    },
                    'payloadSizeDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    }
                },
                '@type:liveappsim': {
                    'app': {
                        'fidelity': {
                        },
                        'removeUnknownSSL': {
                        },
                        'removeUnknownTcpUdp': {
                        },
                        'removedns': {
                        },
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        }
                    },
                    'concurrencyscalefactor': {
                    },
                    'delayStart': {
                    },
                    'inflateDeflate': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'liveProfile': {
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'sfratescalefactor': {
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    },
                    'tputscalefactor': {
                    }
                },
                '@type:playback': {
                    'behavior': {
                    },
                    'delayStart': {
                    },
                    'file': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'modification': {
                        'bpfstring': {
                        },
                        'endpacket': {
                        },
                        'independentflows': {
                        },
                        'loopcount': {
                        },
                        'newport': {
                        },
                        'originalport': {
                        },
                        'replay': {
                        },
                        'serveripinjection': {
                        },
                        'single': {
                        },
                        'startpacket': {
                        }
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    }
                },
                '@type:security_all': {
                    'attackPlan': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackProfile': {
                    },
                    'attackRetries': {
                    },
                    'delayStart': {
                    },
                    'maxAttacksPerSecond': {
                    },
                    'maxConcurrAttacks': {
                    },
                    'maxPacketsPerSecond': {
                    },
                    'randomSeed': {
                    }
                },
                '@type:security_np': {
                    'attackPlan': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackProfile': {
                    },
                    'attackRetries': {
                    },
                    'delayStart': {
                    },
                    'randomSeed': {
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'sessions': {
                        'max': {
                        },
                        'maxPerSecond': {
                        }
                    }
                },
                '@type:stackscrambler': {
                    'delayStart': {
                    },
                    'dstPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'hop_limit': {
                        },
                        'traffic_class': {
                        }
                    },
                    'loadprofile': {
                        'label': {
                        },
                        'name': {
                        }
                    },
                    'payload': {
                        'data': {
                        },
                        'transport': {
                        },
                        'type': {
                        }
                    },
                    'payloadSizeDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'prng': {
                        'offset': {
                        },
                        'seed': {
                        }
                    },
                    'rampDist': {
                        'down': {
                        },
                        'downBehavior': {
                        },
                        'steady': {
                        },
                        'steadyBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        }
                    },
                    'rampUpProfile': {
                        'increment': {
                        },
                        'interval': {
                        },
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'scope': {
                        },
                        'type': {
                        },
                        'unit': {
                        },
                        'unlimited': {
                        }
                    },
                    'scrambleOptions': {
                        'badEthType': {
                        },
                        'badGTPFlags': {
                        },
                        'badGTPLen': {
                        },
                        'badGTPNext': {
                        },
                        'badGTPNpdu': {
                        },
                        'badGTPSeqno': {
                        },
                        'badGTPType': {
                        },
                        'badICMPCode': {
                        },
                        'badICMPType': {
                        },
                        'badIPChecksum': {
                        },
                        'badIPFlags': {
                        },
                        'badIPFlowLabel': {
                        },
                        'badIPFragOffset': {
                        },
                        'badIPLength': {
                        },
                        'badIPOptions': {
                        },
                        'badIPProtocol': {
                        },
                        'badIPTOS': {
                        },
                        'badIPTTL': {
                        },
                        'badIPTotalLength': {
                        },
                        'badIPVersion': {
                        },
                        'badL4Checksum': {
                        },
                        'badL4HeaderLength': {
                        },
                        'badSCTPChecksum': {
                        },
                        'badSCTPFlags': {
                        },
                        'badSCTPLength': {
                        },
                        'badSCTPType': {
                        },
                        'badSCTPVerificationTag': {
                        },
                        'badTCPFlags': {
                        },
                        'badTCPOptions': {
                        },
                        'badUrgentPointer': {
                        },
                        'handshakeTCP': {
                        },
                        'maxCorruptions': {
                        }
                    },
                    'sessions': {
                        'allocationOverride': {
                        },
                        'closeFast': {
                        },
                        'emphasis': {
                        },
                        'engine': {
                        },
                        'max': {
                        },
                        'maxActive': {
                        },
                        'maxPerSecond': {
                        },
                        'openFast': {
                        },
                        'statDetail': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'targetPerSecond': {
                        }
                    },
                    'srcPortDist': {
                        'max': {
                        },
                        'min': {
                        },
                        'type': {
                        }
                    },
                    'tcp': {
                        'ack_every_n': {
                        },
                        'add_timestamps': {
                        },
                        'aging_time': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks': {
                        },
                        'delay_acks_ms': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'ecn': {
                        },
                        'handshake_data': {
                        },
                        'initial_receive_window': {
                        },
                        'mss': {
                        },
                        'psh_every_segment': {
                        },
                        'raw_flags': {
                        },
                        'reset_at_end': {
                        },
                        'retries': {
                        },
                        'retry_quantum_ms': {
                        },
                        'shutdown_data': {
                        },
                        'syn_data_padding': {
                        },
                        'tcp_4_way_close': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'tcp_window_scale': {
                        }
                    }
                },
                'active': {
                },
                'author': {
                },
                'clazz': {
                },
                'createdBy': {
                },
                'createdOn': {
                },
                'description': {
                },
                'id': {
                },
                'label': {
                },
                'lockedBy': {
                },
                'operations': {
                    'getComponentPreset': [{
                        '@type:appsim': {
                            'app': {
                                'fidelity': {
                                },
                                'removedns': {
                                },
                                'replace_streams': {
                                },
                                'streamsPerSuperflow': {
                                }
                            },
                            'delayStart': {
                            },
                            'experimental': {
                                'tcpSegmentsBurst': {
                                },
                                'unify_l4_bufs': {
                                }
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'profile': {
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'resources': {
                                'expand': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'ssl': {
                                'client_record_len': {
                                },
                                'server_record_len': {
                                },
                                'sslReuseType': {
                                },
                                'ssl_client_keylog': {
                                },
                                'ssl_keylog_max_entries': {
                                },
                                'upgrade': {
                                }
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            }
                        },
                        '@type:clientsim': {
                            'app': {
                                'fidelity': {
                                },
                                'removedns': {
                                },
                                'replace_streams': {
                                },
                                'streamsPerSuperflow': {
                                }
                            },
                            'delayStart': {
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'resources': {
                                'expand': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'ssl': {
                                'client_record_len': {
                                },
                                'server_record_len': {
                                },
                                'sslReuseType': {
                                },
                                'ssl_client_keylog': {
                                },
                                'ssl_keylog_max_entries': {
                                },
                                'upgrade': {
                                }
                            },
                            'superflow': {
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            }
                        },
                        '@type:layer2': {
                            'advanced': {
                                'ethTypeField': {
                                },
                                'ethTypeVal': {
                                }
                            },
                            'bidirectional': {
                            },
                            'delayStart': {
                            },
                            'duration': {
                                'disable_nd_probes': {
                                },
                                'durationFrames': {
                                },
                                'durationTime': {
                                }
                            },
                            'maxStreams': {
                            },
                            'payload': {
                                'data': {
                                },
                                'dataWidth': {
                                },
                                'type': {
                                }
                            },
                            'payloadAdvanced': {
                                'udfDataWidth': {
                                },
                                'udfLength': {
                                },
                                'udfMode': {
                                },
                                'udfOffset': {
                                }
                            },
                            'rateDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'ramptype': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'sizeDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'mixlen1': {
                                },
                                'mixlen10': {
                                },
                                'mixlen2': {
                                },
                                'mixlen3': {
                                },
                                'mixlen4': {
                                },
                                'mixlen5': {
                                },
                                'mixlen6': {
                                },
                                'mixlen7': {
                                },
                                'mixlen8': {
                                },
                                'mixlen9': {
                                },
                                'mixweight1': {
                                },
                                'mixweight10': {
                                },
                                'mixweight2': {
                                },
                                'mixweight3': {
                                },
                                'mixweight4': {
                                },
                                'mixweight5': {
                                },
                                'mixweight6': {
                                },
                                'mixweight7': {
                                },
                                'mixweight8': {
                                },
                                'mixweight9': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'slowStart': {
                            },
                            'slowStartFps': {
                            }
                        },
                        '@type:layer3': {
                            'Templates': {
                                'TemplateType': {
                                }
                            },
                            'addrGenMode': {
                            },
                            'advancedIPv4': {
                                'checksumField': {
                                },
                                'checksumVal': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                },
                                'optionHeaderData': {
                                },
                                'optionHeaderField': {
                                },
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'advancedIPv6': {
                                'extensionHeaderData': {
                                },
                                'extensionHeaderField': {
                                },
                                'flowLabel': {
                                },
                                'hopLimit': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                },
                                'nextHeader': {
                                },
                                'trafficClass': {
                                }
                            },
                            'advancedUDP': {
                                'checksumField': {
                                },
                                'checksumVal': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                }
                            },
                            'bidirectional': {
                            },
                            'delayStart': {
                            },
                            'dstPort': {
                            },
                            'dstPortMask': {
                            },
                            'duration': {
                                'disable_nd_probes': {
                                },
                                'durationFrames': {
                                },
                                'durationTime': {
                                }
                            },
                            'enableTCP': {
                            },
                            'maxStreams': {
                            },
                            'payload': {
                                'data': {
                                },
                                'dataWidth': {
                                },
                                'type': {
                                }
                            },
                            'payloadAdvanced': {
                                'udfDataWidth': {
                                },
                                'udfLength': {
                                },
                                'udfMode': {
                                },
                                'udfOffset': {
                                }
                            },
                            'randomizeIP': {
                            },
                            'rateDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'ramptype': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'sizeDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'mixlen1': {
                                },
                                'mixlen10': {
                                },
                                'mixlen2': {
                                },
                                'mixlen3': {
                                },
                                'mixlen4': {
                                },
                                'mixlen5': {
                                },
                                'mixlen6': {
                                },
                                'mixlen7': {
                                },
                                'mixlen8': {
                                },
                                'mixlen9': {
                                },
                                'mixweight1': {
                                },
                                'mixweight10': {
                                },
                                'mixweight2': {
                                },
                                'mixweight3': {
                                },
                                'mixweight4': {
                                },
                                'mixweight5': {
                                },
                                'mixweight6': {
                                },
                                'mixweight7': {
                                },
                                'mixweight8': {
                                },
                                'mixweight9': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'slowStart': {
                            },
                            'slowStartFps': {
                            },
                            'srcPort': {
                            },
                            'srcPortMask': {
                            },
                            'syncIP': {
                            },
                            'udpDstPortMode': {
                            },
                            'udpSrcPortMode': {
                            }
                        },
                        '@type:layer3advanced': {
                            'Templates': {
                                'TemplateType': {
                                }
                            },
                            'advancedIPv4': {
                                'checksumField': {
                                },
                                'checksumVal': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                },
                                'optionHeaderData': {
                                },
                                'optionHeaderField': {
                                },
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'advancedIPv6': {
                                'extensionHeaderData': {
                                },
                                'extensionHeaderField': {
                                },
                                'flowLabel': {
                                },
                                'hopLimit': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                },
                                'nextHeader': {
                                },
                                'trafficClass': {
                                }
                            },
                            'advancedUDP': {
                                'checksumField': {
                                },
                                'checksumVal': {
                                },
                                'lengthField': {
                                },
                                'lengthVal': {
                                }
                            },
                            'bidirectional': {
                            },
                            'delayStart': {
                            },
                            'duration': {
                                'disable_nd_probes': {
                                },
                                'durationFrames': {
                                },
                                'durationTime': {
                                }
                            },
                            'enablePerStreamStats': {
                            },
                            'enableTCP': {
                            },
                            'payload': {
                                'data': {
                                },
                                'dataWidth': {
                                },
                                'type': {
                                }
                            },
                            'payloadAdvanced': {
                                'udfDataWidth': {
                                },
                                'udfLength': {
                                },
                                'udfMode': {
                                },
                                'udfOffset': {
                                }
                            },
                            'rateDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'ramptype': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'sizeDist': {
                                'increment': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'mixlen1': {
                                },
                                'mixlen10': {
                                },
                                'mixlen2': {
                                },
                                'mixlen3': {
                                },
                                'mixlen4': {
                                },
                                'mixlen5': {
                                },
                                'mixlen6': {
                                },
                                'mixlen7': {
                                },
                                'mixlen8': {
                                },
                                'mixlen9': {
                                },
                                'mixweight1': {
                                },
                                'mixweight10': {
                                },
                                'mixweight2': {
                                },
                                'mixweight3': {
                                },
                                'mixweight4': {
                                },
                                'mixweight5': {
                                },
                                'mixweight6': {
                                },
                                'mixweight7': {
                                },
                                'mixweight8': {
                                },
                                'mixweight9': {
                                },
                                'rate': {
                                },
                                'type': {
                                },
                                'unit': {
                                }
                            },
                            'slowStart': {
                            },
                            'slowStartFps': {
                            },
                            'tuple_gen_seed': {
                            }
                        },
                        '@type:layer4': {
                            'delayStart': {
                            },
                            'dstPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'packetsPerSession': {
                            },
                            'payload': {
                                'add_timestamp': {
                                },
                                'data': {
                                },
                                'http_type': {
                                },
                                'transport': {
                                },
                                'type': {
                                }
                            },
                            'payloadSizeDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            }
                        },
                        '@type:liveappsim': {
                            'app': {
                                'fidelity': {
                                },
                                'removeUnknownSSL': {
                                },
                                'removeUnknownTcpUdp': {
                                },
                                'removedns': {
                                },
                                'replace_streams': {
                                },
                                'streamsPerSuperflow': {
                                }
                            },
                            'concurrencyscalefactor': {
                            },
                            'delayStart': {
                            },
                            'inflateDeflate': {
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'liveProfile': {
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'sfratescalefactor': {
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            },
                            'tputscalefactor': {
                            }
                        },
                        '@type:playback': {
                            'behavior': {
                            },
                            'delayStart': {
                            },
                            'file': {
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'modification': {
                                'bpfstring': {
                                },
                                'endpacket': {
                                },
                                'independentflows': {
                                },
                                'loopcount': {
                                },
                                'newport': {
                                },
                                'originalport': {
                                },
                                'replay': {
                                },
                                'serveripinjection': {
                                },
                                'single': {
                                },
                                'startpacket': {
                                }
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            }
                        },
                        '@type:security_all': {
                            'attackPlan': {
                            },
                            'attackPlanIterationDelay': {
                            },
                            'attackPlanIterations': {
                            },
                            'attackProfile': {
                            },
                            'attackRetries': {
                            },
                            'delayStart': {
                            },
                            'maxAttacksPerSecond': {
                            },
                            'maxConcurrAttacks': {
                            },
                            'maxPacketsPerSecond': {
                            },
                            'randomSeed': {
                            }
                        },
                        '@type:security_np': {
                            'attackPlan': {
                            },
                            'attackPlanIterationDelay': {
                            },
                            'attackPlanIterations': {
                            },
                            'attackProfile': {
                            },
                            'attackRetries': {
                            },
                            'delayStart': {
                            },
                            'randomSeed': {
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'sessions': {
                                'max': {
                                },
                                'maxPerSecond': {
                                }
                            }
                        },
                        '@type:stackscrambler': {
                            'delayStart': {
                            },
                            'dstPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'ip': {
                                'tos': {
                                },
                                'ttl': {
                                }
                            },
                            'ip6': {
                                'flowlabel': {
                                },
                                'hop_limit': {
                                },
                                'traffic_class': {
                                }
                            },
                            'loadprofile': {
                                'label': {
                                },
                                'name': {
                                }
                            },
                            'payload': {
                                'data': {
                                },
                                'transport': {
                                },
                                'type': {
                                }
                            },
                            'payloadSizeDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'prng': {
                                'offset': {
                                },
                                'seed': {
                                }
                            },
                            'rampDist': {
                                'down': {
                                },
                                'downBehavior': {
                                },
                                'steady': {
                                },
                                'steadyBehavior': {
                                },
                                'synRetryMode': {
                                },
                                'up': {
                                },
                                'upBehavior': {
                                }
                            },
                            'rampUpProfile': {
                                'increment': {
                                },
                                'interval': {
                                },
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'rateDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'scope': {
                                },
                                'type': {
                                },
                                'unit': {
                                },
                                'unlimited': {
                                }
                            },
                            'scrambleOptions': {
                                'badEthType': {
                                },
                                'badGTPFlags': {
                                },
                                'badGTPLen': {
                                },
                                'badGTPNext': {
                                },
                                'badGTPNpdu': {
                                },
                                'badGTPSeqno': {
                                },
                                'badGTPType': {
                                },
                                'badICMPCode': {
                                },
                                'badICMPType': {
                                },
                                'badIPChecksum': {
                                },
                                'badIPFlags': {
                                },
                                'badIPFlowLabel': {
                                },
                                'badIPFragOffset': {
                                },
                                'badIPLength': {
                                },
                                'badIPOptions': {
                                },
                                'badIPProtocol': {
                                },
                                'badIPTOS': {
                                },
                                'badIPTTL': {
                                },
                                'badIPTotalLength': {
                                },
                                'badIPVersion': {
                                },
                                'badL4Checksum': {
                                },
                                'badL4HeaderLength': {
                                },
                                'badSCTPChecksum': {
                                },
                                'badSCTPFlags': {
                                },
                                'badSCTPLength': {
                                },
                                'badSCTPType': {
                                },
                                'badSCTPVerificationTag': {
                                },
                                'badTCPFlags': {
                                },
                                'badTCPOptions': {
                                },
                                'badUrgentPointer': {
                                },
                                'handshakeTCP': {
                                },
                                'maxCorruptions': {
                                }
                            },
                            'sessions': {
                                'allocationOverride': {
                                },
                                'closeFast': {
                                },
                                'emphasis': {
                                },
                                'engine': {
                                },
                                'max': {
                                },
                                'maxActive': {
                                },
                                'maxPerSecond': {
                                },
                                'openFast': {
                                },
                                'statDetail': {
                                },
                                'target': {
                                },
                                'targetMatches': {
                                },
                                'targetPerSecond': {
                                }
                            },
                            'srcPortDist': {
                                'max': {
                                },
                                'min': {
                                },
                                'type': {
                                }
                            },
                            'tcp': {
                                'ack_every_n': {
                                },
                                'add_timestamps': {
                                },
                                'aging_time': {
                                },
                                'aging_time_data_type': {
                                },
                                'delay_acks': {
                                },
                                'delay_acks_ms': {
                                },
                                'disable_ack_piggyback': {
                                },
                                'dynamic_receive_window_size': {
                                },
                                'ecn': {
                                },
                                'handshake_data': {
                                },
                                'initial_receive_window': {
                                },
                                'mss': {
                                },
                                'psh_every_segment': {
                                },
                                'raw_flags': {
                                },
                                'reset_at_end': {
                                },
                                'retries': {
                                },
                                'retry_quantum_ms': {
                                },
                                'shutdown_data': {
                                },
                                'syn_data_padding': {
                                },
                                'tcp_4_way_close': {
                                },
                                'tcp_connect_delay_ms': {
                                },
                                'tcp_icw': {
                                },
                                'tcp_keepalive_timer': {
                                },
                                'tcp_window_scale': {
                                }
                            }
                        },
                        'active': {
                        },
                        'author': {
                        },
                        'clazz': {
                        },
                        'createdBy': {
                        },
                        'createdOn': {
                        },
                        'description': {
                        },
                        'id': {
                        },
                        'label': {
                        },
                        'lockedBy': {
                        },
                        'originalPreset': {
                        },
                        'originalPresetLabel': {
                        },
                        'reportResults': {
                        },
                        'revision': {
                        },
                        'tags': [{
                            'domainId': {
                                'external': {
                                },
                                'iface': {
                                },
                                'name': {
                                }
                            },
                            'id': {
                            },
                            'type': {
                            }
                        }],
                        'timeline': {
                            'timesegment': [{
                                'label': {
                                },
                                'size': {
                                },
                                'type': {
                                }
                            }]
                        },
                        'type': {
                        }
                    }],
                    'getComponentPresetNames': [{
                    }]
                },
                'originalPreset': {
                },
                'originalPresetLabel': {
                },
                'reportResults': {
                },
                'revision': {
                },
                'tags': [{
                    'domainId': {
                        'external': {
                        },
                        'iface': {
                        },
                        'name': {
                        }
                    },
                    'id': {
                    },
                    'type': {
                    }
                }],
                'timeline': {
                    'timesegment': [{
                        'label': {
                        },
                        'size': {
                        },
                        'type': {
                        }
                    }]
                },
                'type': {
                }
            }],
            'createdBy': {
            },
            'createdOn': {
            },
            'description': {
            },
            'duration': {
            },
            'dut': {
            },
            'label': {
            },
            'lastrun': {
            },
            'lastrunby': {
            },
            'lockedBy': {
            },
            'name': {
            },
            'network': {
            },
            'operations': {
                'add': [{
                }],
                'addOpenRecent': [{
                }],
                'clone': [{
                }],
                'delete': [{
                }],
                'exportModel': [{
                }],
                'flowExceptions': [{
                    'component': {
                    },
                    'componentLabel': {
                    },
                    'componentType': {
                        'label': {
                        }
                    },
                    'dataIndex': {
                    },
                    'group': {
                    },
                    'iface': {
                    },
                    'params': {
                    },
                    'protocol': {
                    },
                    'slot': {
                    },
                    'vlan': {
                    }
                }],
                'getRecent': [{
                }],
                'importModel': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'realTimeStats': [{
                }],
                'remove': [{
                }],
                'run': [{
                }],
                'save': [{
                }],
                'saveAs': [{
                }],
                'search': [{
                }],
                'stopRun': [{
                }],
                'testComponentDefinition': [{
                }],
                'validate': [{
                    'fixAction': {
                        'content': {
                        },
                        'key': {
                        }
                    },
                    'fixable': {
                    },
                    'message': {
                        'content': {
                        },
                        'key': {
                        }
                    },
                    'result': {
                    }
                }]
            },
            'result': {
            },
            'revision': {
            },
            'sharedComponentSettings': {
                'maxFlowCreationRate': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'maximumConcurrentFlows': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'samplePeriod': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'totalAddresses': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'totalAttacks': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'totalBandwidth': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                }
            },
            'summaryInfo': {
                'requiredMTU': {
                },
                'totalMacAddresses': {
                },
                'totalSubnets': {
                },
                'totalUniqueStrikes': {
                },
                'totalUniqueSuperflows': {
                }
            },
            'testComponentTypesDescription': [{
                'description': {
                },
                'label': {
                },
                'name': {
                },
                'template': {
                },
                'type': {
                }
            }]
        },
        'topology': {
            'chain': {
                'name': {
                },
                'remotes': [{
                    'host': {
                    },
                    'state': {
                    }
                }]
            },
            'cnState': [{
                'cnId': {
                },
                'cnName': {
                },
                'cnSerial': {
                },
                'cnSlotNo': {
                },
                'firmwareUpgrade': {
                },
                'licensed': {
                },
                'marketingName': {
                },
                'opModes': [{
                    'active': {
                    },
                    'id': {
                    },
                    'label': {
                    },
                    'name': {
                    }
                }],
                'state': {
                }
            }],
            'ixos': {
            },
            'ixoslicensed': {
            },
            'model': {
            },
            'operations': {
                'addPortNote': [{
                }],
                'addResourceNote': [{
                }],
                'exportCapture': [{
                }],
                'getFanoutModes': [{
                    'cardModel': {
                    },
                    'fanout': [{
                        'fanoutId': {
                        },
                        'name': {
                        }
                    }]
                }],
                'getPortAvailableModes': [{
                    'modes': [{
                        'fanoutId': {
                        },
                        'name': {
                        }
                    }],
                    'port': {
                    },
                    'slot': {
                    }
                }],
                'reboot': [{
                }],
                'rebootComputeNode': [{
                }],
                'releaseAllCnResources': [{
                }],
                'releaseResource': [{
                }],
                'releaseResources': [{
                }],
                'reserve': [{
                }],
                'reserveAllCnResources': [{
                }],
                'reserveResource': [{
                }],
                'reserveResources': [{
                }],
                'run': [{
                }],
                'setCardFanout': [{
                }],
                'setCardMode': [{
                }],
                'setCardSpeed': [{
                }],
                'setPerfAcc': [{
                }],
                'setPortFanoutMode': [{
                }],
                'setPortSettings': [{
                }],
                'softReboot': [{
                }],
                'stopRun': [{
                }],
                'unreserve': [{
                }]
            },
            'resourceOverview': {
                'resourceOverviewList': [{
                    'l23Count': {
                    },
                    'l47Count': {
                    },
                    'portCount': {
                    },
                    'userAndGroup': {
                    }
                }]
            },
            'runningTest': [{
                'capturing': {
                },
                'completed': {
                },
                'currentTest': {
                },
                'initProgress': {
                },
                'label': {
                },
                'phase': {
                },
                'port': [{
                }],
                'progress': {
                },
                'reservedEngines': [{
                }],
                'result': {
                },
                'runtime': {
                },
                'state': {
                },
                'testid': {
                    'host': {
                    },
                    'iteration': {
                    },
                    'name': {
                    }
                },
                'timeRemaining': {
                },
                'user': {
                }
            }],
            'serialNumber': {
            },
            'slot': [{
                'firmwareUpgrade': {
                },
                'fpga': [{
                    'group': {
                    },
                    'id': {
                    },
                    'name': {
                    },
                    'note': {
                    },
                    'reservedBy': {
                    },
                    'resourceType': {
                    },
                    'state': {
                    }
                }],
                'id': {
                },
                'interfaceCount': {
                },
                'mode': {
                },
                'model': {
                },
                'np': [{
                    'cnId': {
                    },
                    'group': {
                    },
                    'id': {
                    },
                    'name': {
                    },
                    'note': {
                    },
                    'reservedBy': {
                    },
                    'resourceType': {
                    },
                    'state': {
                    }
                }],
                'opModes': [{
                    'active': {
                    },
                    'id': {
                    },
                    'label': {
                    },
                    'name': {
                    }
                }],
                'port': [{
                    'active': {
                    },
                    'auto': {
                    },
                    'capture': {
                    },
                    'capturing': {
                    },
                    'currentMode': {
                    },
                    'exportProgress': {
                    },
                    'fullduplex': {
                    },
                    'group': {
                    },
                    'id': {
                    },
                    'ifmacaddr': {
                    },
                    'ifname': {
                    },
                    'ignorepause': {
                    },
                    'link': {
                    },
                    'media': {
                    },
                    'model': {
                    },
                    'mtu': {
                    },
                    'note': {
                    },
                    'number': {
                    },
                    'owner': {
                    },
                    'pcap': [{
                        'rxbytes': {
                        },
                        'rxframes': {
                        },
                        'txbytes': {
                        },
                        'txframes': {
                        }
                    }],
                    'portGroup': {
                    },
                    'possibleModes': {
                    },
                    'precoder': {
                    },
                    'reservedBy': {
                    },
                    'speed': {
                    },
                    'state': {
                    }
                }],
                'remoteInfo': {
                    'host': {
                    },
                    'slotId': {
                    },
                    'state': {
                    }
                },
                'serialNumber': {
                },
                'state': {
                }
            }]
        }
    }

    def __call__(cls, *args, **kwds):
        return DataModelMeta._decorate_model_object(type.__call__(cls, *args, **kwds))

    @staticmethod
    def _decorate_model_object(obj):
        obj_name = obj._name
        (data_model_path, data_model) = DataModelMeta._get_from_model(obj.__data_model_path__())
        if data_model is None:
            return obj
        if isinstance(data_model, list):
            setattr(obj, '_getitem_', lambda x: DataModelProxy(wrapper=obj._wrapper, name=str(x), path=obj.__full_path__(), model_path=obj.__data_model_path__()))
            if data_model_path.endswith(obj_name):
                DataModelMeta._decorate_model_object_operations(data_model[0], data_model_path, obj)
                return obj
            else:
                data_model = data_model[0]
        DataModelMeta._decorate_model_object_operations(data_model, data_model_path,  obj)
        for key in data_model:
            if key.startswith("@") or key == 'operations':
                continue
            setattr(obj, key, DataModelProxy(wrapper=obj._wrapper, name=key, path=obj.__full_path__(), model_path=obj.__data_model_path__()))
        if obj_name not in data_model:
            for key in data_model:
                if not key.startswith("@") or ":" not in key:
                    continue
                [fieldName, fieldValue] = key.split(":")
                fieldName = fieldName.replace("@", "")
                try:
                    if obj.__cached_get__(fieldName) != fieldValue:
                        continue
                except:
                    continue
                for extField in data_model[key]:
                    ext_path = obj.__full_path__()
                    ext_dm_path = obj.__data_model_path__() + "/" + key
                    setattr(obj, extField, DataModelProxy(wrapper=obj._wrapper, name=extField, path=ext_path, model_path=ext_dm_path))
        return obj

    @staticmethod
    def _decorate_model_object_operations(data_model, data_model_path, obj):
        if 'operations' not in data_model:
            return
        for operation in data_model['operations']:
            if obj.__full_path__().replace("/", "") == '':
                continue
            method_name = data_model_path.replace("/", "_") + '_operations_' + operation
            setattr(obj, operation, obj._wrapper.__getattribute__(method_name).__get__(obj))
            setattr(getattr(obj, operation).__func__, '__name__', operation)

    @staticmethod
    def _get_from_model(path):
        model_data = DataModelMeta._dataModel
        model_path = ""
        for path_part in path.split('/'):
            if len(path_part) == 0: continue
            if isinstance(model_data, list):
                model_data = model_data[0]
                continue
            if path_part not in model_data: return (None, None)
            model_data = model_data[path_part]
            model_path = model_path + "/" + path_part
        return (model_path, model_data)

class DataModelProxy(object, metaclass = DataModelMeta):

    def __init__(self, wrapper, name,  path='', model_path=None):
        self.__cache = {}
        self._wrapper = wrapper
        self._name = name
        self._path = path
        if model_path is None:
            self._model_path = self._path
        else:
            self._model_path = model_path

    def __cached_get__(self, field):
        if field not in self.__cache: self.__cache[field] = self._wrapper._BPS__get(self.__data_model_path__()+"/"+field)
        return self.__cache[field]

    def __data_model_path__(self):
        return '%s/%s' % (self._model_path, self._name)

    def __full_path__(self):
        return '%s/%s' % (self._path, self._name)

    def __getitem__(self, item):
        return self._getitem_(item)

    def __repr__(self):
        return 'proxy object for \'%s\' ' % (self.__url__())

    def __url__(self):
        return 'https://%s/bps/api/v2/core%s' % (self._wrapper.host, self.__full_path__())

    def delete(self):
        return self._wrapper._BPS__delete(self._path+'/'+self._name)

    def get(self, responseDepth=None, **kwargs):
        return self._wrapper._BPS__get(self._path+'/'+self._name, responseDepth, **kwargs)

    def help(self):
        doc_data = self._wrapper._BPS__options(self._path+'/'+self._name)
        if doc_data and 'custom' in doc_data:
            doc_data = doc_data['custom']
        if doc_data and 'description' in doc_data:
            print(doc_data['description'])

    def patch(self, value):
        return self._wrapper._BPS__patch(self._path+'/'+self._name, value)

    def put(self, value):
        return self._wrapper._BPS__put(self._path+'/'+self._name, value)

    def set(self, value):
        return self.patch(value)
