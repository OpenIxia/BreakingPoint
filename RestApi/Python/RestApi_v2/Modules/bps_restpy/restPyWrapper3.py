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

### this BPS REST API wrapper is generated for version: 9.37.0.129
class BPS(object):

    def __init__(self, host, user, password, checkVersion=True):
        self.host = host
        self.user = user
        self.password = password
        self.sessionId = None
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter())
        self.clientVersion = '9.37'
        self.serverVersions = None
        self.checkVersion = checkVersion
        self.testmodel = DataModelProxy(wrapper=self, name='testmodel')
        self.superflow = DataModelProxy(wrapper=self, name='superflow')
        self.loadProfile = DataModelProxy(wrapper=self, name='loadProfile')
        self.strikeList = DataModelProxy(wrapper=self, name='strikeList')
        self.appProfile = DataModelProxy(wrapper=self, name='appProfile')
        self.capture = DataModelProxy(wrapper=self, name='capture')
        self.administration = DataModelProxy(wrapper=self, name='administration')
        self.network = DataModelProxy(wrapper=self, name='network')
        self.topology = DataModelProxy(wrapper=self, name='topology')
        self.evasionProfile = DataModelProxy(wrapper=self, name='evasionProfile')
        self.strikes = DataModelProxy(wrapper=self, name='strikes')
        self.reports = DataModelProxy(wrapper=self, name='reports')
        self.statistics = DataModelProxy(wrapper=self, name='statistics')
        self.results = DataModelProxy(wrapper=self, name='results')

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

    def printVersions(self):
        apiServerVersion = 'N/A'
        if self.serverVersions != None and 'apiServer' in self.serverVersions:
            apiServerVersion = self.serverVersions['apiServer']
        print('Client version: %s \nServer version: %s' % (self.clientVersion, apiServerVersion))

    def __json_load(self, r):
        try:
            return r.json()
        except:
            return r.content.decode() if r.content is not None else None

    ### login into the bps system
    def login(self):
        self.__connect()
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/login', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        if(r.status_code == 200):
            self.serverVersions = self.__json_load(r)
            apiServerVersion = 'N/A'
            if self.serverVersions != None and 'apiServer' in self.serverVersions:
                apiServerVersion = self.serverVersions['apiServer']
            if self.checkVersion:
                if not apiServerVersion.startswith(self.clientVersion):
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

    ### Get from data model
    def _get(self, path, responseDepth=None, **kwargs):
        requestUrl = 'https://%s/bps/api/v2/core%s%s' % (self.host, path, '?responseDepth=%s' % responseDepth if responseDepth else '')
        for key, value in kwargs.items():
            requestUrl = requestUrl + "&%s=%s" % (key, value)
        headers = {'content-type': 'application/json'}
        r = self.session.get(url=requestUrl, headers=headers, verify=False)
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def _patch(self, path, value):
        r = self.session.patch(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def _put(self, path, value):
        r = self.session.put(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### Get from data model
    def _delete(self, path):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/'+ path
        headers = {'content-type': 'application/json'}
        r = self.session.delete(url=requestUrl, headers=headers, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### OPTIONS request
    def _options(self, path):
        r = self.session.options('https://' + self.host + '/bps/api/v2/core/'+ path)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### generic post operation
    def _post(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        r = self.session.post(url=requestUrl, headers={'content-type': 'application/json'}, data=json.dumps(kwargs), verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204, 202]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### generic import operation
    def _import(self, path, filename, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        files = {'file': (kwargs['name'], open(filename, 'rb'), 'application/xml')}
        r = self.session.post(url=requestUrl, files=files, data={'fileInfo':str(kwargs)}, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        if(r.status_code in [200, 204]):
            return self.__json_load(r)
        raise Exception({'status_code': r.status_code, 'content': self.__json_load(r)})

    ### generic post operation
    def _export(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
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

    ### Deletes a given Strike List from the database.
    @staticmethod
    def _strikeList_operations_delete(self, name):
        """
        Deletes a given Strike List from the database.
        :param name (string): The name of the Strike List to be deleted.
        """
        return self._wrapper._post('/strikeList/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _evasionProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search evasion profile name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by. (name/createdBy ...)
        :param sortorder (string): The sort order (ascending/descending)
        :return results (list): 
               list of object with fields
                      name (string): 
                      label (string): 
                      createdBy (string): 
                      revision (number): 
                      description (string): 
        """
        return self._wrapper._post('/evasionProfile/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Stops the test run.
    @staticmethod
    def _testmodel_operations_stopRun(self, runid):
        """
        Stops the test run.
        :param runid (number): Test RUN ID
        """
        return self._wrapper._post('/testmodel/operations/stopRun', **{'runid': runid})

    ### Stops the test run.
    @staticmethod
    def _topology_operations_stopRun(self, runid):
        """
        Stops the test run.
        :param runid (number): Test RUN ID
        """
        return self._wrapper._post('/topology/operations/stopRun', **{'runid': runid})

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
        return self._wrapper._export('/reports/operations/exportReport', **{'filepath': filepath, 'runid': runid, 'reportType': reportType, 'sectionIds': sectionIds, 'dataType': dataType})

    ### Get available port fan-out modes.
    @staticmethod
    def _topology_operations_getPortAvailableModes(self, cardId, port):
        """
        Get available port fan-out modes.
        :param cardId (number): Slot id
        :param port (number): Port id to be interrogated
        :return modes (object): Available port switch modes.
        """
        return self._wrapper._post('/topology/operations/getPortAvailableModes', **{'cardId': cardId, 'port': port})

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
        return self._wrapper._post('/superflow/operations/addFlow', **{'flowParams': flowParams})

    ### Reserves the specified number of resources of given type.
    @staticmethod
    def _topology_operations_reserveResources(self, group, count, resourceType):
        """
        Reserves the specified number of resources of given type.
        :param group (number): 
        :param count (number): 
        :param resourceType (string): 
        """
        return self._wrapper._post('/topology/operations/reserveResources', **{'group': group, 'count': count, 'resourceType': resourceType})

    ### Lists all the component presets names.
    @staticmethod
    def _testmodel_component_operations_getComponentPresetNames(self, type='None'):
        """
        Lists all the component presets names.
        :param type (string): The Component type.
        All the component types are listed under the node testComponentTypesDescription.
        If this argument is not set, all the presets will be listed.
        :return result (list): 
               list of object with fields
                      id (string): 
                      label (string): 
                      type (string): 
                      description (string): 
        """
        return self._wrapper._post('/testmodel/component/operations/getComponentPresetNames', **{'type': type})

    ### Load an existing Application Profile and sets it as the current one.
    @staticmethod
    def _appProfile_operations_load(self, template):
        """
        Load an existing Application Profile and sets it as the current one.
        :param template (string): The name of the template application profile
        """
        return self._wrapper._post('/appProfile/operations/load', **{'template': template})

    ### Creates a new Application Profile.
    @staticmethod
    def _appProfile_operations_new(self, template=None):
        """
        Creates a new Application Profile.
        :param template (string): This argument must remain unset. Do not set any value for it.
        """
        return self._wrapper._post('/appProfile/operations/new', **{'template': template})

    ### Imports a list of strikes residing in a file.
    @staticmethod
    def _strikeList_operations_importStrikeList(self, name, filename, force):
        """
        Imports a list of strikes residing in a file.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object to be imported.
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/strikeList/operations/importStrikeList', **{'name': name, 'filename': filename, 'force': force})

    ### null
    @staticmethod
    def _loadProfile_operations_save(self):
        return self._wrapper._post('/loadProfile/operations/save', **{})

    ### Save the active editing LoadProfile under specified name
    @staticmethod
    def _loadProfile_operations_saveAs(self, name):
        """
        Save the active editing LoadProfile under specified name
        :param name (string): 
        """
        return self._wrapper._post('/loadProfile/operations/saveAs', **{'name': name})

    ### Imports a test model, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _testmodel_operations_importModel(self, name, filename, force):
        """
        Imports a test model, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/testmodel/operations/importModel', **{'name': name, 'filename': filename, 'force': force})

    ### Imports an application profile, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _appProfile_operations_importAppProfile(self, name, filename, force):
        """
        Imports an application profile, given as a file. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/appProfile/operations/importAppProfile', **{'name': name, 'filename': filename, 'force': force})

    ### Imports a network neighborhood model, given as a file.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _network_operations_importNetwork(self, name, filename, force):
        """
        Imports a network neighborhood model, given as a file.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and replace the object having the same name.
        """
        return self._wrapper._import('/network/operations/importNetwork', **{'name': name, 'filename': filename, 'force': force})

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
        return self._wrapper._post('/network/operations/list', **{'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset})

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
        :return results (list): 
               list of object with fields
                      name (string): 
                      label (string): 
                      createdBy (string): 
                      revision (number): 
                      description (string): 
        """
        return self._wrapper._post('/network/operations/search', **{'searchString': searchString, 'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset})

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
        return self._wrapper._export('/topology/operations/exportCapture', **{'filepath': filepath, 'args': args})

    ### Deletes a Test Report from the database.
    @staticmethod
    def _reports_operations_delete(self, runid):
        """
        Deletes a Test Report from the database.
        :param runid (number): The test run id that generated the report you want to delete.
        """
        return self._wrapper._post('/reports/operations/delete', **{'runid': runid})

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
        return self._wrapper._post('/topology/operations/addPortNote', **{'interface': interface, 'note': note})

    ### Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
    @staticmethod
    def _strikeList_operations_remove(self, strike):
        """
        Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
        :param strike (list): The list of strike ids to remove. The strike id is in fact the it's path.
               list of object with fields
                      id (string): 
        """
        return self._wrapper._post('/strikeList/operations/remove', **{'strike': strike})

    ### Adds a note to given resource.
    @staticmethod
    def _topology_operations_addResourceNote(self, resourceId, resourceType):
        """
        Adds a note to given resource.
        :param resourceId (string): Resource Id.
        :param resourceType (string): Resource type.
        """
        return self._wrapper._post('/topology/operations/addResourceNote', **{'resourceId': resourceId, 'resourceType': resourceType})

    ### Deletes a specified load profile from the database.
    @staticmethod
    def _loadProfile_operations_delete(self, name):
        """
        Deletes a specified load profile from the database.
        :param name (string): The name of the loadProfile object to delete.
        """
        return self._wrapper._post('/loadProfile/operations/delete', **{'name': name})

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
        return self._wrapper._post('/superflow/operations/addHost', **{'hostParams': hostParams, 'force': force})

    ### null
    @staticmethod
    def _reports_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search test name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by: 'name'/'endTime'/'duration'/'result'/'startTime'/'iteration'/'network'/'dut'/'user'/'size'
        :param sortorder (string): The sort order: ascending/descending 
        """
        return self._wrapper._post('/reports/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

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
        return self._wrapper._post('/testmodel/operations/realTimeStats', **{'runid': runid, 'rtsgroup': rtsgroup, 'numSeconds': numSeconds, 'numDataPoints': numDataPoints})

    ### Reserves all l47 resources of given compute node id.
    @staticmethod
    def _topology_operations_reserveAllCnResources(self, group, cnId):
        """
        Reserves all l47 resources of given compute node id.
        :param group (number): 
        :param cnId (string): 
        """
        return self._wrapper._post('/topology/operations/reserveAllCnResources', **{'group': group, 'cnId': cnId})

    ### Deletes a given Super Flow from the database.
    @staticmethod
    def _superflow_operations_delete(self, name):
        """
        Deletes a given Super Flow from the database.
        :param name (string): The name of the Super Flow.
        """
        return self._wrapper._post('/superflow/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _superflow_flows_operations_getFlowChoices(self, id, name):
        """
        :param id (number): The flow id.
        :param name (string): The flow type/name.
        :return result (list): 
        """
        return self._wrapper._post('/superflow/flows/operations/getFlowChoices', **{'id': id, 'name': name})

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
        return self._wrapper._import('/superflow/operations/importResource', **{'name': name, 'filename': filename, 'force': force, 'type': type})

    ### Saves the working network config and gives it a new name.
    @staticmethod
    def _network_operations_saveAs(self, name, regenerateOldStyle=True, force=False):
        """
        Saves the working network config and gives it a new name.
        :param name (string): The new name given for the current working network config
        :param regenerateOldStyle (bool): Force to apply the changes made on the loaded network configuration. Force to generate a network from the old one.
        :param force (bool): Force to save the network config. It replaces a pre-existing config having the same name.
        """
        return self._wrapper._post('/network/operations/saveAs', **{'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force})

    ### Save the current working network config.
    @staticmethod
    def _network_operations_save(self, name=None, regenerateOldStyle=True, force=True):
        """
        Save the current working network config.
        :param name (string): The new name given for the current working network config. No need to configure. The current name is used.
        :param regenerateOldStyle (bool): No need to configure. The default is used.
        :param force (bool): No need to configure. The default is used.
        """
        return self._wrapper._post('/network/operations/save', **{'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force})

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
        :return results (list): 
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
        return self._wrapper._post('/strikes/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder, 'offset': offset})

    ### Sets the card mode of a board.
    @staticmethod
    def _topology_operations_setCardMode(self, board, mode):
        """
        Sets the card mode of a board.
        :param board (number): Slot ID.
        :param mode (number): The new mode: 10(BPS-L23), 7(BPS L4-7), 3(IxLoad), 
        		11(BPS QT L2-3), 12(BPS QT L4-7) 
        """
        return self._wrapper._post('/topology/operations/setCardMode', **{'board': board, 'mode': mode})

    ### Sets the card speed of a board
    @staticmethod
    def _topology_operations_setCardSpeed(self, board, speed):
        """
        Sets the card speed of a board
        :param board (number): Slot ID.
        :param speed (number): The new speed.(the int value for 1G is 1000, 10G(10000), 40G(40000))
        """
        return self._wrapper._post('/topology/operations/setCardSpeed', **{'board': board, 'speed': speed})

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
        return self._wrapper._post('/topology/operations/setCardFanout', **{'board': board, 'fanid': fanid})

    ### Enables/Disables the performance acceleration for a BPS VE blade.
    @staticmethod
    def _topology_operations_setPerfAcc(self, board, perfacc):
        """
        Enables/Disables the performance acceleration for a BPS VE blade.
        :param board (number): Slot ID.
        :param perfacc (bool): Boolean value: 'True' to enable the performance Acceleration and 'False' otherwise. 
        """
        return self._wrapper._post('/topology/operations/setPerfAcc', **{'board': board, 'perfacc': perfacc})

    ### null
    @staticmethod
    def _administration_userSettings_operations_setAutoReserve(self, resourceType, units):
        """
        :param resourceType (string): Valid values: >l47< or >l23<
        :param units (number): 
        """
        return self._wrapper._post('/administration/userSettings/operations/setAutoReserve', **{'resourceType': resourceType, 'units': units})

    ### null
    @staticmethod
    def _topology_operations_releaseResources(self, count, resourceType):
        """
        :param count (number): 
        :param resourceType (string): 
        """
        return self._wrapper._post('/topology/operations/releaseResources', **{'count': count, 'resourceType': resourceType})

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
        return self._wrapper._post('/superflow/operations/addAction', **{'flowid': flowid, 'type': type, 'actionid': actionid, 'source': source})

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
        return self._wrapper._post('/reports/operations/getReportContents', **{'runid': runid, 'getTableOfContents': getTableOfContents})

    ### Returns the section of a report
    @staticmethod
    def _reports_operations_getReportTable(self, runid, sectionId):
        """
        Returns the section of a report
        :param runid (number): The test run id.
        :param sectionId (string): The section id of the table desired to extract.
        :return results (object): 
        """
        return self._wrapper._post('/reports/operations/getReportTable', **{'runid': runid, 'sectionId': sectionId})

    ### Loads an existing network config by name.
    @staticmethod
    def _network_operations_load(self, template):
        """
        Loads an existing network config by name.
        :param template (string): The name of the network neighborhood template
        """
        return self._wrapper._post('/network/operations/load', **{'template': template})

    ### Creates a new Network Neighborhood configuration with no name. The template value must remain empty.
    @staticmethod
    def _network_operations_new(self, template=None):
        """
        Creates a new Network Neighborhood configuration with no name. The template value must remain empty.
        :param template (string): The name of the template. In this case will be empty. No need to configure.
        """
        return self._wrapper._post('/network/operations/new', **{'template': template})

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _appProfile_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Application Profile
        :param force (bool): Force to save the working Application Profile using the given name.
        """
        return self._wrapper._post('/appProfile/operations/saveAs', **{'name': name, 'force': force})

    ### Saves the current working application profile using the current name. No need to use any parameter.
    @staticmethod
    def _appProfile_operations_save(self, name=None, force=True):
        """
        Saves the current working application profile using the current name. No need to use any parameter.
        :param name (string): The name of the template. No need to configure. The current name is used.
        :param force (bool): Force to save the working Application Profile with the same name. No need to configure. The default is used.
        """
        return self._wrapper._post('/appProfile/operations/save', **{'name': name, 'force': force})

    ### Deletes a given Evasion Profile from the database.
    @staticmethod
    def _evasionProfile_operations_delete(self, name):
        """
        Deletes a given Evasion Profile from the database.
        :param name (string): The name of the profile to delete.
        """
        return self._wrapper._post('/evasionProfile/operations/delete', **{'name': name})

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
        return self._wrapper._export('/testmodel/operations/exportModel', **{'name': name, 'attachments': attachments, 'filepath': filepath, 'runid': runid})

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
        return self._wrapper._post('/administration/operations/logs', **{'error': error, 'messages': messages, 'web': web, 'all': all, 'audit': audit, 'info': info, 'system': system, 'lines': lines, 'drop': drop})

    ### Reboots the slot with slotId.
    @staticmethod
    def _topology_operations_reboot(self, board):
        """
        Reboots the slot with slotId.
        :param board (number): 
        """
        return self._wrapper._post('/topology/operations/reboot', **{'board': board})

    ### Recompute percentages in the current working Application Profile
    @staticmethod
    def _appProfile_operations_recompute(self):
        """
        Recompute percentages in the current working Application Profile
        """
        return self._wrapper._post('/appProfile/operations/recompute', **{})

    ### null
    @staticmethod
    def _topology_operations_releaseResource(self, group, resourceId, resourceType):
        """
        :param group (number): 
        :param resourceId (number): 
        :param resourceType (string): 
        """
        return self._wrapper._post('/topology/operations/releaseResource', **{'group': group, 'resourceId': resourceId, 'resourceType': resourceType})

    ### null
    @staticmethod
    def _topology_operations_setPortSettings(self, linkState, slotId, portId):
        """
        :param linkState (string): 
        :param slotId (number): 
        :param portId (number): 
        """
        return self._wrapper._post('/topology/operations/setPortSettings', **{'linkState': linkState, 'slotId': slotId, 'portId': portId})

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
        return self._wrapper._post('/appProfile/operations/add', **{'add': add})

    ### Sets a User Preference.
    @staticmethod
    def _administration_userSettings_operations_changeUserSetting(self, name, value):
        """
        Sets a User Preference.
        :param name (string): The setting name.
        :param value (string): The new value for setting.
        """
        return self._wrapper._post('/administration/userSettings/operations/changeUserSetting', **{'name': name, 'value': value})

    ### Retrieves all the security options
    @staticmethod
    def _evasionProfile_StrikeOptions_operations_getStrikeOptions(self):
        """
        Retrieves all the security options
        :return result (list): 
        """
        return self._wrapper._post('/evasionProfile/StrikeOptions/operations/getStrikeOptions', **{})

    ### null
    @staticmethod
    def _results_operations_getHistoricalResultSize(self, runid, componentid, group):
        """
        :param runid (number): The test run id
        :param componentid (string): The component identifier
        :param group (string): The data group or one of the BPS component main groups. The group name can be get by executing the operation 'getGroups' from results node
        :return result (string): 
        """
        return self._wrapper._post('/results/operations/getHistoricalResultSize', **{'runid': runid, 'componentid': componentid, 'group': group})

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _superflow_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Super Flow
        :param force (bool): Force to save the working Super Flow using the given name.
        """
        return self._wrapper._post('/superflow/operations/saveAs', **{'name': name, 'force': force})

    ### Saves the working Super Flow using the current name
    @staticmethod
    def _superflow_operations_save(self, name=None, force=True):
        """
        Saves the working Super Flow using the current name
        :param name (string): The name of the template that should be empty.
        :param force (bool): Force to save the working Super Flow with the same name.
        """
        return self._wrapper._post('/superflow/operations/save', **{'name': name, 'force': force})

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
        return self._wrapper._post('/testmodel/operations/add', **{'name': name, 'component': component, 'type': type, 'active': active})

    ### Removes an action from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeAction(self, id):
        """
        Removes an action from the current working SuperFlow.
        :param id (number): The action ID.
        """
        return self._wrapper._post('/superflow/operations/removeAction', **{'id': id})

    ### Runs a Test.
    @staticmethod
    def _testmodel_operations_run(self, modelname, group, allowMalware=False):
        """
        Runs a Test.
        :param modelname (string): Test Name to run
        :param group (number): Group to run
        :param allowMalware (bool): Enable this option to allow malware in test.
        """
        return self._wrapper._post('/testmodel/operations/run', **{'modelname': modelname, 'group': group, 'allowMalware': allowMalware})

    ### Runs a Test.
    @staticmethod
    def _topology_operations_run(self, modelname, group, allowMalware=False):
        """
        Runs a Test.
        :param modelname (string): Test Name to run
        :param group (number): Group to run
        :param allowMalware (bool): Enable this option to allow malware in test.
        """
        return self._wrapper._post('/topology/operations/run', **{'modelname': modelname, 'group': group, 'allowMalware': allowMalware})

    ### Saves the current working Test Model under specified name.
    @staticmethod
    def _testmodel_operations_saveAs(self, name, force):
        """
        Saves the current working Test Model under specified name.
        :param name (string): The new name given for the current working Test Model
        :param force (bool): Force to save the working Test Model using a new name.
        """
        return self._wrapper._post('/testmodel/operations/saveAs', **{'name': name, 'force': force})

    ### Saves the working Test Model using the current name. No need to configure. The current name is used.
    @staticmethod
    def _testmodel_operations_save(self, name=None, force=True):
        """
        Saves the working Test Model using the current name. No need to configure. The current name is used.
        :param name (string): The name of the template that should be empty.
        :param force (bool): Force to save the working Test Model with the same name.
        """
        return self._wrapper._post('/testmodel/operations/save', **{'name': name, 'force': force})

    ### Imports a capture file to the systemThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _capture_operations_importCapture(self, name, filename, force):
        """
        Imports a capture file to the systemThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the capture being imported
        :param filename (string): The file containing the capture object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/capture/operations/importCapture', **{'name': name, 'filename': filename, 'force': force})

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
        return self._wrapper._post('/superflow/actions/operations/getActionInfo', **{'id': id})

    ### Gets the card Fanout modes of a board.
    @staticmethod
    def _topology_operations_getFanoutModes(self, cardId):
        """
        Gets the card Fanout modes of a board.
        :param cardId (number): Slot ID.
        :return modes (object): Fanout mode id per card type.
        """
        return self._wrapper._post('/topology/operations/getFanoutModes', **{'cardId': cardId})

    ### Imports an ATI License file (.lic) on a hardware platform. This operation is NOT recommended to be used on BPS Virtual platforms.
    @staticmethod
    def _administration_atiLicensing_operations_importAtiLicense(self, filename, name):
        """
        Imports an ATI License file (.lic) on a hardware platform. This operation is NOT recommended to be used on BPS Virtual platforms.
        :param filename (string): import file path
        :param name (string): the name of the license file
        """
        return self._wrapper._import('/administration/atiLicensing/operations/importAtiLicense', **{'filename': filename, 'name': name})

    ### Load an existing Super Flow and sets it as the current one.
    @staticmethod
    def _superflow_operations_load(self, template):
        """
        Load an existing Super Flow and sets it as the current one.
        :param template (string): The name of the existing Super Flow template
        """
        return self._wrapper._post('/superflow/operations/load', **{'template': template})

    ### Creates a new Super Flow.
    @staticmethod
    def _superflow_operations_new(self, template=None):
        """
        Creates a new Super Flow.
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper._post('/superflow/operations/new', **{'template': template})

    ### Deletes a given Test Model from the database.
    @staticmethod
    def _testmodel_operations_delete(self, name):
        """
        Deletes a given Test Model from the database.
        :param name (string): The name of the Test Model.
        """
        return self._wrapper._post('/testmodel/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _capture_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search capture name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :return results (list): 
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
        return self._wrapper._post('/capture/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### null
    @staticmethod
    def _topology_operations_unreserve(self, unreservation):
        """
        :param unreservation (list): 
               list of object with fields
                      slot (number): 
                      port (number): 
        """
        return self._wrapper._post('/topology/operations/unreserve', **{'unreservation': unreservation})

    ### Deletes a given Network Neighborhood Config from the database.
    @staticmethod
    def _network_operations_delete(self, name):
        """
        Deletes a given Network Neighborhood Config from the database.
        :param name (string): The name of the Network Neighborhood Config.
        """
        return self._wrapper._post('/network/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _superflow_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search Super Flow name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        """
        return self._wrapper._post('/superflow/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Load an existing test model template.
    @staticmethod
    def _testmodel_operations_load(self, template):
        """
        Load an existing test model template.
        :param template (string): The name of the template testmodel
        """
        return self._wrapper._post('/testmodel/operations/load', **{'template': template})

    ### Creates a new Test Model
    @staticmethod
    def _testmodel_operations_new(self, template=None):
        """
        Creates a new Test Model
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper._post('/testmodel/operations/new', **{'template': template})

    ### Reboots the compute node with cnId.
    @staticmethod
    def _topology_operations_rebootComputeNode(self, cnId):
        """
        Reboots the compute node with cnId.
        :param cnId (number): Compute node id
        """
        return self._wrapper._post('/topology/operations/rebootComputeNode', **{'cnId': cnId})

    ### Removes a flow from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeFlow(self, id):
        """
        Removes a flow from the current working SuperFlow.
        :param id (number): The flow ID.
        """
        return self._wrapper._post('/superflow/operations/removeFlow', **{'id': id})

    ### Imports all test models, actually imports everything from 'exportAllTests'. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _administration_operations_importAllTests(self, name, filename, force):
        """
        Imports all test models, actually imports everything from 'exportAllTests'. This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): String name to append to each test name.
        :param filename (string): The file containing the object.
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/administration/operations/importAllTests', **{'name': name, 'filename': filename, 'force': force})

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
        return self._wrapper._post('/topology/operations/reserve', **{'reservation': reservation, 'force': force})

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
        return self._wrapper._post('/strikeList/operations/add', **{'strike': strike, 'validate': validate, 'toList': toList})

    ### Reboots the metwork processors on the given card card. Only available for APS cards.
    @staticmethod
    def _topology_operations_softReboot(self, board):
        """
        Reboots the metwork processors on the given card card. Only available for APS cards.
        :param board (number): 
        """
        return self._wrapper._post('/topology/operations/softReboot', **{'board': board})

    ### Reserves the specified resource of the given type.
    @staticmethod
    def _topology_operations_reserveResource(self, group, resourceId, resourceType):
        """
        Reserves the specified resource of the given type.
        :param group (number): 
        :param resourceId (number): 
        :param resourceType (string): 
        """
        return self._wrapper._post('/topology/operations/reserveResource', **{'group': group, 'resourceId': resourceId, 'resourceType': resourceType})

    ### null
    @staticmethod
    def _topology_operations_releaseAllCnResources(self, cnId):
        """
        :param cnId (string): 
        """
        return self._wrapper._post('/topology/operations/releaseAllCnResources', **{'cnId': cnId})

    ### Returns stats series for a given component group stat output for a given timestamp
    @staticmethod
    def _results_operations_getHistoricalSeries(self, runid, componentid, dataindex, group):
        """
        Returns stats series for a given component group stat output for a given timestamp
        :param runid (number): The test identifier
        :param componentid (string): The component identifier. Each component has an id and can be get loading the testand checking it's components info
        :param dataindex (number): The table index, equivalent with timestamp.
        :param group (string): The data group or one of the BPS component main groups. The group name can be get by executing the operation 'getGroups' from results node.
        :return results (list): 
               list of object with fields
                      name (string): 
                      content (string): 
                      datasetvals (string): 
        """
        return self._wrapper._post('/results/operations/getHistoricalSeries', **{'runid': runid, 'componentid': componentid, 'dataindex': dataindex, 'group': group})

    ### null
    @staticmethod
    def _loadProfile_operations_load(self, template):
        """
        :param template (string): 
        """
        return self._wrapper._post('/loadProfile/operations/load', **{'template': template})

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
                      groups (object): 
        """
        return self._wrapper._post('/results/operations/getGroups', **{'name': name, 'dynamicEnums': dynamicEnums, 'includeOutputs': includeOutputs})

    ### Saves the current working Test Model under specified name.
    @staticmethod
    def _evasionProfile_operations_saveAs(self, name, force):
        """
        Saves the current working Test Model under specified name.
        :param name (string): The new name given for the current working Evasion Profile
        :param force (bool): Force to save the working Evasion Profile using a new name.
        """
        return self._wrapper._post('/evasionProfile/operations/saveAs', **{'name': name, 'force': force})

    ### Saves the working Test Model using the current name. No need to configure. The current name is used.
    @staticmethod
    def _evasionProfile_operations_save(self, name=None, force=True):
        """
        Saves the working Test Model using the current name. No need to configure. The current name is used.
        :param name (string): This argument should be empty for saving the profile using it's actual name.
        :param force (bool): Force to save the working profile with the same name.
        """
        return self._wrapper._post('/evasionProfile/operations/save', **{'name': name, 'force': force})

    ### null
    @staticmethod
    def _superflow_actions_operations_getActionChoices(self, id):
        """
        :param id (number): the flow id
        """
        return self._wrapper._post('/superflow/actions/operations/getActionChoices', **{'id': id})

    ### Exports the Strike List identified by its name and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _strikeList_operations_exportStrikeList(self, name, filepath):
        """
        Exports the Strike List identified by its name and all of its dependenciesThis operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the strike list to be exported.
        :param filepath (string): The local path where to save the exported object. The file should have .bap extension
        """
        return self._wrapper._export('/strikeList/operations/exportStrikeList', **{'name': name, 'filepath': filepath})

    ### Removes a component from the current working Test Model.
    @staticmethod
    def _testmodel_operations_remove(self, id):
        """
        Removes a component from the current working Test Model.
        :param id (string): The component id.
        """
        return self._wrapper._post('/testmodel/operations/remove', **{'id': id})

    ### Saves the current working Strike List and gives it a new name.
    @staticmethod
    def _strikeList_operations_saveAs(self, name, force):
        """
        Saves the current working Strike List and gives it a new name.
        :param name (string): The new name given for the current working Strike List
        :param force (bool): Force to save the working Strike List using the given name.
        """
        return self._wrapper._post('/strikeList/operations/saveAs', **{'name': name, 'force': force})

    ### Saves the current working Strike List using the current name
    @staticmethod
    def _strikeList_operations_save(self, name=None, force=True):
        """
        Saves the current working Strike List using the current name
        :param name (string): The name of the template. Default is empty.
        :param force (bool): Force to save the working Strike List with the same name.
        """
        return self._wrapper._post('/strikeList/operations/save', **{'name': name, 'force': force})

    ### Deletes a given Application Profile from the database.
    @staticmethod
    def _appProfile_operations_delete(self, name):
        """
        Deletes a given Application Profile from the database.
        :param name (string): The name of the Application Profiles.
        """
        return self._wrapper._post('/appProfile/operations/delete', **{'name': name})

    ### Load an existing Strike List and sets it as the current one.
    @staticmethod
    def _strikeList_operations_load(self, template):
        """
        Load an existing Strike List and sets it as the current one.
        :param template (string): The name of the Strike List template
        """
        return self._wrapper._post('/strikeList/operations/load', **{'template': template})

    ### Creates a new Strike List.
    @staticmethod
    def _strikeList_operations_new(self, template=None):
        """
        Creates a new Strike List.
        :param template (string): The name of the template. In this case will be empty.
        """
        return self._wrapper._post('/strikeList/operations/new', **{'template': template})

    ### Load an existing Evasion Profile and sets it as the current one.
    @staticmethod
    def _evasionProfile_operations_load(self, template):
        """
        Load an existing Evasion Profile and sets it as the current one.
        :param template (string): The name of an Evasion profile template.
        """
        return self._wrapper._post('/evasionProfile/operations/load', **{'template': template})

    ### Creates a new Evasion Profile.
    @staticmethod
    def _evasionProfile_operations_new(self, template=None):
        """
        Creates a new Evasion Profile.
        :param template (string): The name should be empty to create a new object.
        """
        return self._wrapper._post('/evasionProfile/operations/new', **{'template': template})

    ### Exports everything including test models, network configurations and others from system.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _administration_operations_exportAllTests(self, filepath):
        """
        Exports everything including test models, network configurations and others from system.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param filepath (string): The local path where to save the compressed file with all the models. The path must contain the file name and extension (.tar.gz): '/d/c/f/AllTests.tar.gz'
        """
        return self._wrapper._export('/administration/operations/exportAllTests', **{'filepath': filepath})

    ### null
    @staticmethod
    def _strikeList_operations_search(self, searchString='', limit=10, sort='name', sortorder='ascending'):
        """
        :param searchString (string): Search strike list name matching the string given.
        :param limit (number): The limit of rows to return
        :param sort (string): Parameter to sort by. Default is by name.
        :param sortorder (string): The sort order (ascending/descending). Default is ascending.
        """
        return self._wrapper._post('/strikeList/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Create a new custom Load Profile.
    @staticmethod
    def _loadProfile_operations_createNewCustom(self, loadProfile):
        """
        Create a new custom Load Profile.
        :param loadProfile (string): The Name of The load profile object to create.
        """
        return self._wrapper._post('/loadProfile/operations/createNewCustom', **{'loadProfile': loadProfile})

    ### null
    @staticmethod
    def _testmodel_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search test name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by: 'createdOn'/'timestamp'/'bandwidth'/'result'/'lastrunby'/'createdBy'/'interfaces'/'testLabType'
        :param sortorder (string): The sort order: ascending/descending 
        :return results (list): 
               list of object with fields
                      name (string): 
                      label (string): 
                      createdBy (string): 
                      network (string): 
                      duration (number): 
                      description (string): 
        """
        return self._wrapper._post('/testmodel/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

    ### Gives abbreviated information about all Canned Flow Names.
    @staticmethod
    def _superflow_flows_operations_getCannedFlows(self):
        """
        Gives abbreviated information about all Canned Flow Names.
        :return results (list): 
               list of object with fields
                      name (string): 
                      label (string): 
        """
        return self._wrapper._post('/superflow/flows/operations/getCannedFlows', **{})

    ### Exports an Application profile and all of its dependencies.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
    @staticmethod
    def _appProfile_operations_exportAppProfile(self, name, attachments, filepath):
        """
        Exports an Application profile and all of its dependencies.This operation can not be executed from the RESTApi Browser, it needs to be executed from a remote system through a REST call.
        :param name (string): The name of the test model to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        """
        return self._wrapper._export('/appProfile/operations/exportAppProfile', **{'name': name, 'attachments': attachments, 'filepath': filepath})

    ### Switch port fan-out mode.
    @staticmethod
    def _topology_operations_setPortFanoutMode(self, board, port, mode):
        """
        Switch port fan-out mode.
        :param board (number): 
        :param port (string): 
        :param mode (string): 
        """
        return self._wrapper._post('/topology/operations/setPortFanoutMode', **{'board': board, 'port': port, 'mode': mode})

    ### Clones a component in the current working Test Model
    @staticmethod
    def _testmodel_operations_clone(self, template, type, active):
        """
        Clones a component in the current working Test Model
        :param template (string): The ID of the test component to clone.
        :param type (string): Component Type: appsim, sesionsender ..
        :param active (bool): Set component enable (by default is active) or disable
        """
        return self._wrapper._post('/testmodel/operations/clone', **{'template': template, 'type': type, 'active': active})

    ### Removes a SuperFlow from the current working Application Profile. 
    @staticmethod
    def _appProfile_operations_remove(self, superflow):
        """
        Removes a SuperFlow from the current working Application Profile. 
        :param superflow (string): The name of the super flow.
        """
        return self._wrapper._post('/appProfile/operations/remove', **{'superflow': superflow})

    ### null
    @staticmethod
    def _appProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (string): Search application profile name matching the string given.
        :param limit (string): The limit of rows to return
        :param sort (string): Parameter to sort by.
        :param sortorder (string): The sort order (ascending/descending)
        :return results (list): 
               list of object with fields
                      name (string): 
                      label (string): 
                      createdBy (string): 
                      revision (number): 
                      description (string): 
        """
        return self._wrapper._post('/appProfile/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

class DataModelMeta(type):
    _dataModel = {
        'testmodel': {
            'lastrunby': {
            },
            'summaryInfo': {
                'totalSubnets': {
                },
                'totalMacAddresses': {
                },
                'totalUniqueStrikes': {
                },
                'totalUniqueSuperflows': {
                },
                'requiredMTU': {
                }
            },
            'author': {
            },
            'lastrun': {
            },
            'description': {
            },
            'label': {
            },
            'sharedComponentSettings': {
                'maximumConcurrentFlows': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                },
                'totalAttacks': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                },
                'totalBandwidth': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                },
                'maxFlowCreationRate': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                },
                'totalAddresses': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                },
                'samplePeriod': {
                    'current': {
                    },
                    'original': {
                    },
                    'content': {
                    }
                }
            },
            'createdOn': {
            },
            'network': {
            },
            'revision': {
            },
            'duration': {
            },
            'result': {
            },
            'component': [{
                'author': {
                },
                'originalPreset': {
                },
                'active': {
                },
                'originalPresetLabel': {
                },
                'description': {
                },
                'label': {
                },
                'type': {
                },
                '@type:liveappsim': {
                    'app': {
                        'removeUnknownTcpUdp': {
                        },
                        'replace_streams': {
                        },
                        'removeUnknownSSL': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'inflateDeflate': {
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
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
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'tputscalefactor': {
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'concurrencyscalefactor': {
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'sfratescalefactor': {
                    },
                    'liveProfile': {
                    }
                },
                '@type:layer3advanced': {
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'bidirectional': {
                    },
                    'enableTCP': {
                    },
                    'slowStart': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'enablePerStreamStats': {
                    },
                    'tuple_gen_seed': {
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'advancedIPv4': {
                        'lengthVal': {
                        },
                        'optionHeaderField': {
                        },
                        'optionHeaderData': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'tos': {
                        },
                        'checksumField': {
                        },
                        'ttl': {
                        }
                    },
                    'advancedIPv6': {
                        'flowLabel': {
                        },
                        'lengthVal': {
                        },
                        'extensionHeaderField': {
                        },
                        'lengthField': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        },
                        'extensionHeaderData': {
                        },
                        'hopLimit': {
                        }
                    }
                },
                '@type:appsim': {
                    'app': {
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'profile': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'resources': {
                        'expand': {
                        }
                    },
                    'experimental': {
                        'tcpSegmentsBurst': {
                        },
                        'unify_l4_bufs': {
                        }
                    },
                    'ssl': {
                        'ssl_client_keylog': {
                        },
                        'upgrade': {
                        },
                        'sslReuseType': {
                        },
                        'server_record_len': {
                        },
                        'client_record_len': {
                        },
                        'ssl_keylog_max_entries': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    }
                },
                '@type:security_all': {
                    'maxConcurrAttacks': {
                    },
                    'attackRetries': {
                    },
                    'maxPacketsPerSecond': {
                    },
                    'attackPlan': {
                    },
                    'randomSeed': {
                    },
                    'delayStart': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'maxAttacksPerSecond': {
                    }
                },
                '@type:security_np': {
                    'attackRetries': {
                    },
                    'sessions': {
                        'max': {
                        },
                        'maxPerSecond': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'attackPlan': {
                    },
                    'randomSeed': {
                    },
                    'delayStart': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackPlanIterationDelay': {
                    }
                },
                '@type:layer3': {
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'bidirectional': {
                    },
                    'randomizeIP': {
                    },
                    'enableTCP': {
                    },
                    'slowStart': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'srcPort': {
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'udpSrcPortMode': {
                    },
                    'dstPort': {
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    },
                    'syncIP': {
                    },
                    'addrGenMode': {
                    },
                    'maxStreams': {
                    },
                    'dstPortMask': {
                    },
                    'udpDstPortMode': {
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'advancedIPv4': {
                        'lengthVal': {
                        },
                        'optionHeaderField': {
                        },
                        'optionHeaderData': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'tos': {
                        },
                        'checksumField': {
                        },
                        'ttl': {
                        }
                    },
                    'srcPortMask': {
                    },
                    'advancedIPv6': {
                        'flowLabel': {
                        },
                        'lengthVal': {
                        },
                        'extensionHeaderField': {
                        },
                        'lengthField': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        },
                        'extensionHeaderData': {
                        },
                        'hopLimit': {
                        }
                    }
                },
                '@type:layer4': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
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
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
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
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'packetsPerSession': {
                    },
                    'payloadSizeDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:playback': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'modification': {
                        'startpacket': {
                        },
                        'originalport': {
                        },
                        'newport': {
                        },
                        'replay': {
                        },
                        'bpfstring': {
                        },
                        'single': {
                        },
                        'loopcount': {
                        },
                        'endpacket': {
                        },
                        'independentflows': {
                        },
                        'serveripinjection': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'file': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'behavior': {
                    }
                },
                '@type:layer2': {
                    'bidirectional': {
                    },
                    'maxStreams': {
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'advanced': {
                        'ethTypeField': {
                        },
                        'ethTypeVal': {
                        }
                    },
                    'slowStart': {
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    }
                },
                '@type:stackscrambler': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'scrambleOptions': {
                        'maxCorruptions': {
                        },
                        'badIPFlags': {
                        },
                        'badIPFragOffset': {
                        },
                        'badIPLength': {
                        },
                        'badUrgentPointer': {
                        },
                        'badIPFlowLabel': {
                        },
                        'badEthType': {
                        },
                        'badTCPOptions': {
                        },
                        'badGTPNext': {
                        },
                        'handshakeTCP': {
                        },
                        'badIPChecksum': {
                        },
                        'badSCTPLength': {
                        },
                        'badTCPFlags': {
                        },
                        'badICMPType': {
                        },
                        'badIPTTL': {
                        },
                        'badIPProtocol': {
                        },
                        'badSCTPFlags': {
                        },
                        'badGTPFlags': {
                        },
                        'badIPVersion': {
                        },
                        'badL4HeaderLength': {
                        },
                        'badL4Checksum': {
                        },
                        'badIPOptions': {
                        },
                        'badSCTPType': {
                        },
                        'badSCTPChecksum': {
                        },
                        'badGTPNpdu': {
                        },
                        'badICMPCode': {
                        },
                        'badSCTPVerificationTag': {
                        },
                        'badIPTOS': {
                        },
                        'badIPTotalLength': {
                        },
                        'badGTPLen': {
                        },
                        'badGTPType': {
                        },
                        'badGTPSeqno': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
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
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'prng': {
                        'seed': {
                        },
                        'offset': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'payload': {
                        'data': {
                        },
                        'transport': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'payloadSizeDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:clientsim': {
                    'app': {
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_icw': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'syn_data_padding': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'resources': {
                        'expand': {
                        }
                    },
                    'ssl': {
                        'ssl_client_keylog': {
                        },
                        'upgrade': {
                        },
                        'sslReuseType': {
                        },
                        'server_record_len': {
                        },
                        'client_record_len': {
                        },
                        'ssl_keylog_max_entries': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'superflow': {
                    }
                },
                'createdOn': {
                },
                'tags': [{
                    'id': {
                    },
                    'type': {
                    },
                    'domainId': {
                        'name': {
                        },
                        'iface': {
                        },
                        'external': {
                        }
                    }
                }],
                'revision': {
                },
                'lockedBy': {
                },
                'createdBy': {
                },
                'reportResults': {
                },
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
                'id': {
                },
                'contentType': {
                },
                'operations': {
                    'getComponentPresetNames': [{
                    }]
                }
            }],
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'contentType': {
            },
            'testComponentTypesDescription': [{
                'template': {
                },
                'name': {
                },
                'description': {
                },
                'label': {
                },
                'type': {
                }
            }],
            'operations': {
                'stopRun': [{
                }],
                'importModel': [{
                }],
                'realTimeStats': [{
                }],
                'exportModel': [{
                }],
                'add': [{
                }],
                'run': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'delete': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'remove': [{
                }],
                'search': [{
                }],
                'clone': [{
                }]
            }
        },
        'superflow': {
            'actions': [{
                'actionInfo': [{
                    'name': {
                    },
                    'description': {
                    },
                    'realtimeGroup': {
                    },
                    'label': {
                    },
                    'units': {
                    }
                }],
                'flowlabel': {
                },
                'gotoBlock': {
                },
                'exflows': {
                },
                'matchBlock': {
                },
                'id': {
                },
                'source': {
                },
                'label': {
                },
                'type': {
                },
                'params': {
                },
                'flowid': {
                },
                'operations': {
                    'getActionInfo': [{
                        'name': {
                        },
                        'description': {
                        },
                        'realtimeGroup': {
                        },
                        'label': {
                        },
                        'units': {
                        }
                    }],
                    'getActionChoices': [{
                    }]
                }
            }],
            'settings': [{
                'name': {
                },
                'description': {
                },
                'realtimeGroup': {
                },
                'label': {
                },
                'units': {
                }
            }],
            'percentFlows': {
            },
            'seed': {
            },
            'hosts': [{
                'iface': {
                },
                'hostname': {
                },
                'ip': {
                    'type': {
                    }
                },
                'id': {
                }
            }],
            'author': {
            },
            'estimate_bytes': {
            },
            'estimate_flows': {
            },
            'weight': {
            },
            'description': {
            },
            'label': {
            },
            'params': {
            },
            'constraints': {
            },
            'createdOn': {
            },
            'revision': {
            },
            'lockedBy': {
            },
            'flows': [{
                'singleNP': {
                },
                'name': {
                },
                'from': {
                },
                'label': {
                },
                'id': {
                },
                'to': {
                },
                'params': {
                },
                'flowcount': {
                },
                'operations': {
                    'getFlowChoices': [{
                        'lockedBy': {
                        },
                        'createdBy': {
                        },
                        'author': {
                        },
                        'description': {
                        },
                        'label': {
                        },
                        'createdOn': {
                        },
                        'contentType': {
                        },
                        'revision': {
                        }
                    }],
                    'getCannedFlows': [{
                    }]
                }
            }],
            'generated': {
            },
            'createdBy': {
            },
            'percentBandwidth': {
            },
            'name': {
            },
            'contentType': {
            },
            'operations': {
                'addFlow': [{
                }],
                'addHost': [{
                }],
                'delete': [{
                }],
                'importResource': [{
                }],
                'addAction': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'removeAction': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }],
                'removeFlow': [{
                }]
            }
        },
        'loadProfile': {
            'presets': [{
                'phase': [{
                    'duration': {
                    },
                    'phaseId': {
                    },
                    'type': {
                    },
                    'sessions.max': {
                    },
                    'sessions.maxPerSecond': {
                    },
                    'rateDist.unit': {
                    },
                    'rateDist.min': {
                    },
                    'rampDist.steadyBehavior': {
                    },
                    'rateDist.type': {
                    },
                    'rateDist.scope': {
                    }
                }],
                'author': {
                },
                'regen': {
                },
                'description': {
                },
                'label': {
                },
                'createdOn': {
                },
                'summaryData': {
                    'deviceType': {
                    },
                    'unknownUdpAppNames': {
                    },
                    'unknownSslSuperflowName': {
                    },
                    'magicNumber': {
                    },
                    'downloadBytesSum': {
                    },
                    'version': {
                    },
                    'phaseDuration': {
                    },
                    'unknownTcpAppNames': {
                    },
                    'uploadBytesSum': {
                    },
                    'summaryName': {
                    },
                    'basisOfRegeneration': {
                    },
                    'activeFlowsSum': {
                    },
                    'miniSlotDuration': {
                    },
                    'unknownSslAppNames': {
                    },
                    'dynamicSuperflowName': {
                    },
                    'appStat': [{
                    }],
                    'startTime': {
                    },
                    'endTime': {
                    },
                    'dynamicAppNames': {
                    }
                },
                'revision': {
                },
                'lockedBy': {
                },
                'createdBy': {
                },
                'name': {
                },
                'contentType': {
                }
            }],
            'phase': [{
                'duration': {
                },
                'phaseId': {
                },
                'type': {
                },
                'sessions.max': {
                },
                'sessions.maxPerSecond': {
                },
                'rateDist.unit': {
                },
                'rateDist.min': {
                },
                'rampDist.steadyBehavior': {
                },
                'rateDist.type': {
                },
                'rateDist.scope': {
                }
            }],
            'author': {
            },
            'regen': {
            },
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'summaryData': {
                'deviceType': {
                },
                'unknownUdpAppNames': {
                },
                'unknownSslSuperflowName': {
                },
                'magicNumber': {
                },
                'downloadBytesSum': {
                },
                'version': {
                },
                'phaseDuration': {
                },
                'unknownTcpAppNames': {
                },
                'uploadBytesSum': {
                },
                'summaryName': {
                },
                'basisOfRegeneration': {
                },
                'activeFlowsSum': {
                },
                'miniSlotDuration': {
                },
                'unknownSslAppNames': {
                },
                'dynamicSuperflowName': {
                },
                'appStat': [{
                }],
                'startTime': {
                },
                'endTime': {
                },
                'dynamicAppNames': {
                }
            },
            'revision': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'contentType': {
            },
            'operations': {
                'save': [{
                }],
                'saveAs': [{
                }],
                'delete': [{
                }],
                'load': [{
                }],
                'createNewCustom': [{
                }]
            }
        },
        'strikeList': {
            'author': {
            },
            'description': {
            },
            'label': {
            },
            'queryString': {
            },
            'SecurityBehavior': {
            },
            'strikes': [{
                'path': {
                },
                'strike': {
                },
                'strikeset': {
                }
            }],
            'StrikeOptions': {
            },
            'createdOn': {
            },
            'revision': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'contentType': {
            },
            'numStrikes': {
            },
            'operations': {
                'delete': [{
                }],
                'importStrikeList': [{
                }],
                'remove': [{
                }],
                'add': [{
                }],
                'exportStrikeList': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }]
            }
        },
        'appProfile': {
            'weightType': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'author': {
            },
            'name': {
            },
            'superflow': [{
                'settings': [{
                    'name': {
                    },
                    'description': {
                    },
                    'realtimeGroup': {
                    },
                    'label': {
                    },
                    'units': {
                    }
                }],
                'percentFlows': {
                },
                'seed': {
                },
                'author': {
                },
                'estimate_bytes': {
                },
                'estimate_flows': {
                },
                'weight': {
                },
                'description': {
                },
                'label': {
                },
                'params': {
                },
                'constraints': {
                },
                'createdOn': {
                },
                'revision': {
                },
                'lockedBy': {
                },
                'generated': {
                },
                'createdBy': {
                },
                'percentBandwidth': {
                },
                'name': {
                },
                'contentType': {
                }
            }],
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'contentType': {
            },
            'revision': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'importAppProfile': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'recompute': [{
                }],
                'add': [{
                }],
                'delete': [{
                }],
                'exportAppProfile': [{
                }],
                'remove': [{
                }],
                'search': [{
                }]
            }
        },
        'capture': {
            'pcapFilesize': {
            },
            'avgPacketSize': {
            },
            'author': {
            },
            'udpPackets': {
            },
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'name': {
            },
            'revision': {
            },
            'duration': {
            },
            'ipv4Packets': {
            },
            'ipv6Packets': {
            },
            'lockedBy': {
            },
            'tcpPackets': {
            },
            'createdBy': {
            },
            'avgFlowLength': {
            },
            'totalPackets': {
            },
            'contentType': {
            },
            'operations': {
                'importCapture': [{
                }],
                'search': [{
                }]
            }
        },
        'administration': {
            'userSettings': [{
                'name': {
                },
                'content': {
                },
                'operations': {
                    'setAutoReserve': [{
                    }],
                    'changeUserSetting': [{
                    }]
                }
            }],
            'atiLicensing': {
                'license': [{
                    'expires': {
                    },
                    'issuedBy': {
                    },
                    'name': {
                    },
                    'boardserialno': {
                    },
                    'issued': {
                    },
                    'slotNo': {
                    },
                    'maintenance': {
                        'maintenanceExpiration': {
                        }
                    },
                    'serialno': {
                    }
                }],
                'operations': {
                    'importAtiLicense': [{
                    }]
                }
            },
            'systemSettings': {
                'strikepackUpdate': {
                    'password': {
                    },
                    'interval': {
                    },
                    'check': {
                    },
                    'username': {
                    }
                },
                'author': {
                },
                'description': {
                },
                'label': {
                },
                'guardrailSettings': {
                    'enableStrictMode': {
                    },
                    'testStop': {
                    },
                    'testStatusWarning': {
                    },
                    'stopOnLinkdown': {
                    },
                    'testStartPrevention': {
                    }
                },
                'createdOn': {
                },
                'revision': {
                },
                'vacuumSettings': {
                    'vacuumWindowHigh': {
                    },
                    'autoVacuum': {
                    },
                    'vacuumWindowLow': {
                    },
                    'vacuumWindowTZ': {
                    }
                },
                'lockedBy': {
                },
                'createdBy': {
                },
                'softwareUpdate': {
                    'password': {
                    },
                    'interval': {
                    },
                    'check': {
                    },
                    'username': {
                    }
                },
                'contentType': {
                }
            },
            'operations': {
                'logs': [{
                }],
                'importAllTests': [{
                }],
                'exportAllTests': [{
                }]
            }
        },
        'network': {
            'lockedBy': {
            },
            'createdBy': {
            },
            'author': {
            },
            'name': {
            },
            'interfaceCount': {
            },
            'description': {
            },
            'label': {
            },
            'networkModel': {
                'ip_router': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    }
                }],
                'ue_info': [{
                    'imsi_base': {
                    },
                    'secret_key_step': {
                    },
                    'count': {
                    },
                    'operator_variant': {
                    },
                    'secret_key': {
                    },
                    'imei_base': {
                    },
                    'msisdn_base': {
                    },
                    'maxmbps_per_ue': {
                    },
                    'mobility_session_infos': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'id': {
                    }
                }],
                'ip_ldap_server': [{
                    'auth_timeout': {
                    },
                    'ldap_username_start_tag': {
                    },
                    'ldap_user_min': {
                    },
                    'ldap_user_count': {
                    },
                    'authentication_rate': {
                    },
                    'ldap_password_start_tag': {
                    },
                    'ldap_user_max': {
                    },
                    'id': {
                    },
                    'ldap_server_address': {
                    },
                    'dn_fixed_val': {
                    }
                }],
                'mme_sgw_pgw6': [{
                    'ue_info': {
                    },
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'mobility_session_info': [{
                    'password': {
                    },
                    'bearers': [{
                        'qci_label': {
                        }
                    }],
                    'id': {
                    },
                    'access_point_name': {
                    },
                    'username': {
                    },
                    'initiated_dedicated_bearers': {
                    }
                }],
                'ggsn6': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip_static_hosts': [{
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'ip_selection_type': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'maxmbps_per_host': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'ldap': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'dns_proxy': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
                    }
                }],
                'ggsn': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'ue': [{
                    'allocation_rate': {
                    },
                    'mobility_interval_ms': {
                    },
                    'ue_info': {
                    },
                    'dns': {
                    },
                    'mobility_action': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'default_container': {
                    },
                    'mobility_with_traffic': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    },
                    'request_ipv6': {
                    },
                    'enable_stats': {
                    }
                }],
                'enodeb_mme_sgw6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ds_lite_aftr': [{
                    'count': {
                    },
                    'ip_address': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'b4_count': {
                    },
                    'b4_ip_address': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ipsec_router': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'ipsec': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ike_peer_ip_address': {
                    }
                }],
                'dhcpv6c_req_opts_cfg': [{
                    'dhcpv6v_req_preference': {
                    },
                    'dhcpv6v_req_dns_list': {
                    },
                    'dhcpv6v_req_dns_resolvers': {
                    },
                    'dhcpv6v_req_server_id': {
                    },
                    'id': {
                    }
                }],
                'sgsn': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'ggsn_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    }
                }],
                'enodeb_mme6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'enodebs': [{
                        'gateway_ip_address': {
                        },
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'ip_address': {
                        },
                        'prefix_length': {
                        }
                    }],
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'sgw_ip_address': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'plmn': [{
                    'mnc': {
                    },
                    'description': {
                    },
                    'id': {
                    },
                    'mcc': {
                    }
                }],
                'sgw_pgw': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'ip6_dhcp_server': [{
                    'ia_type': {
                    },
                    'pool_size': {
                    },
                    'ip_address': {
                    },
                    'pool_prefix_length': {
                    },
                    'offer_lifetime': {
                    },
                    'max_lease_time': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'pool_base_address': {
                    },
                    'default_lease_time': {
                    },
                    'pool_dns_address1': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'pool_dns_address2': {
                    }
                }],
                'ip6_external_hosts': [{
                    'proxy': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'tags': {
                    }
                }],
                'dhcpv6c_tout_and_retr_cfg': [{
                    'dhcp6c_inforeq_attempts': {
                    },
                    'dhcp6c_initial_rebind_tout': {
                    },
                    'dhcp6c_sol_attempts': {
                    },
                    'dhcp6c_max_rebind_tout': {
                    },
                    'dhcp6c_release_attempts': {
                    },
                    'dhcp6c_initial_release_tout': {
                    },
                    'dhcp6c_req_attempts': {
                    },
                    'dhcp6c_max_req_tout': {
                    },
                    'dhcp6c_max_renew_tout': {
                    },
                    'dhcp6c_max_sol_tout': {
                    },
                    'dhcp6c_initial_req_tout': {
                    },
                    'dhcp6c_max_inforeq_tout': {
                    },
                    'dhcp6c_initial_sol_tout': {
                    },
                    'dhcp6c_initial_renew_tout': {
                    },
                    'dhcp6c_initial_inforeq_tout': {
                    },
                    'id': {
                    }
                }],
                'sgw_pgw6': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'mpls_settings': [{
                    'mpls_tags': [{
                        'mpls_ttl': {
                        },
                        'mpls_label': {
                        },
                        'mpls_exp': {
                        }
                    }],
                    'id': {
                    }
                }],
                'sixrd_ce': [{
                    'sixrd_prefix': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'sixrd_prefix_length': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'br_ip_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'hosts_per_ce': {
                    },
                    'ip4_mask_length': {
                    },
                    'id': {
                    },
                    'enable_stats': {
                    }
                }],
                'ip_dhcp_hosts': [{
                    'allocation_rate': {
                    },
                    'count': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'ldap': {
                    },
                    'default_container': {
                    },
                    'accept_local_offers_only': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    },
                    'dns_proxy': {
                    },
                    'enable_stats': {
                    }
                }],
                'enodeb_mme': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'enodebs': [{
                        'gateway_ip_address': {
                        },
                        'netmask': {
                        },
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'ip_address': {
                        }
                    }],
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'sgw_ip_address': {
                    },
                    'id': {
                    }
                }],
                'enodeb': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'sctp_over_udp': {
                    },
                    'enodebs': [{
                        'mme_ip_address': {
                        },
                        'enodebCount': {
                        },
                        'ip_address': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'sctp_sport': {
                    }
                }],
                'ip6_router': [{
                    'hosts_ip_alloc_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip_external_hosts': [{
                    'proxy': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'tags': {
                    }
                }],
                'interface': [{
                    'ignore_pause_frames': {
                    },
                    'duplicate_mac_address': {
                    },
                    'description': {
                    },
                    'packet_filter': {
                        'not_dest_port': {
                        },
                        'not_src_ip': {
                        },
                        'filter': {
                        },
                        'src_ip': {
                        },
                        'src_port': {
                        },
                        'vlan': {
                        },
                        'not_vlan': {
                        },
                        'dest_ip': {
                        },
                        'not_dest_ip': {
                        },
                        'dest_port': {
                        },
                        'not_src_port': {
                        }
                    },
                    'impairments': {
                        'drop': {
                        },
                        'corrupt_lt64': {
                        },
                        'rate': {
                        },
                        'corrupt_lt256': {
                        },
                        'corrupt_rand': {
                        },
                        'corrupt_chksum': {
                        },
                        'corrupt_gt256': {
                        },
                        'frack': {
                        }
                    },
                    'mtu': {
                    },
                    'vlan_key': {
                    },
                    'number': {
                    },
                    'use_vnic_mac_address': {
                    },
                    'mac_address': {
                    },
                    'id': {
                    }
                }],
                'ds_lite_b4': [{
                    'aftr_addr': {
                    },
                    'count': {
                    },
                    'ip_address': {
                    },
                    'host_ip_base_addr': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'aftr_count': {
                    },
                    'hosts_ip_increment': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'host_ip_addr_alloc_mode': {
                    }
                }],
                'ip_dns_proxy': [{
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'id': {
                    },
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    }
                }],
                'ip6_dns_proxy': [{
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'id': {
                    },
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    }
                }],
                'global_config': [{
                    'gtp': {
                    },
                    'id': {
                    }
                }],
                'vlan': [{
                    'tpid': {
                    },
                    'duplicate_mac_address': {
                    },
                    'description': {
                    },
                    'mtu': {
                    },
                    'outer_vlan': {
                    },
                    'inner_vlan': {
                    },
                    'mac_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'mme_sgw_pgw': [{
                    'ue_info': {
                    },
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'path_advanced': [{
                    'destination_port_count': {
                    },
                    'destination_port_base': {
                    },
                    'source_port_base': {
                    },
                    'tags': {
                    },
                    'enable_external_file': {
                    },
                    'source_container': {
                    },
                    'source_port_algorithm': {
                    },
                    'tuple_limit': {
                    },
                    'file': {
                    },
                    'destination_port_algorithm': {
                    },
                    'destination_container': {
                    },
                    'source_port_count': {
                    },
                    'xor_bits': {
                    },
                    'stream_group': {
                    },
                    'id': {
                    }
                }],
                'path_basic': [{
                    'source_container': {
                    },
                    'destination_container': {
                    },
                    'id': {
                    }
                }],
                'pgw': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'pgw6': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'sgsn6': [{
                    'gateway_ip_address': {
                    },
                    'default_container': {
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
                'ip6_static_hosts': [{
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'ip_alloc_container': {
                    },
                    'ip_selection_type': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'maxmbps_per_host': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'host_ipv6_addr_alloc_mode': {
                    },
                    'prefix_length': {
                    },
                    'dns_proxy': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
                    }
                }],
                'enodeb_mme_sgw': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'enodeb6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'sctp_over_udp': {
                    },
                    'enodebs': [{
                        'mme_ip_address': {
                        },
                        'enodebCount': {
                        },
                        'ip_address': {
                        }
                    }],
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'sctp_sport': {
                    }
                }],
                'slaac_cfg': [{
                    'use_rand_addr': {
                    },
                    'enable_dad': {
                    },
                    'id': {
                    },
                    'stateless_dhcpv6c_cfg': {
                    },
                    'fallback_ip_address': {
                    }
                }],
                'ip_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'ip_dhcp_server': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'lease_time': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'accept_local_requests_only': {
                    }
                }],
                'ip6_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'ipsec_config': [{
                    'ike_dh': {
                    },
                    'ipsec_lifetime': {
                    },
                    'ike_pfs': {
                    },
                    'ike_mode': {
                    },
                    'ike_1to1': {
                    },
                    'nat_traversal': {
                    },
                    'xauth_username': {
                    },
                    'ike_encr_alg': {
                    },
                    'psk': {
                    },
                    'dpd_enabled': {
                    },
                    'dpd_timeout': {
                    },
                    'init_rate': {
                    },
                    'setup_timeout': {
                    },
                    'esp_encr_alg': {
                    },
                    'ike_lifetime': {
                    },
                    'ike_version': {
                    },
                    'id': {
                    },
                    'left_id': {
                    },
                    'ike_prf_alg': {
                    },
                    'esp_auth_alg': {
                    },
                    'dpd_delay': {
                    },
                    'xauth_password': {
                    },
                    'initial_contact': {
                    },
                    'debug_log': {
                    },
                    'wildcard_tsr': {
                    },
                    'rekey_margin': {
                    },
                    'ike_auth_alg': {
                    },
                    'right_id': {
                    },
                    'max_outstanding': {
                    },
                    'retrans_interval': {
                    },
                    'enable_xauth': {
                    }
                }],
                'dhcpv6c_cfg': [{
                    'dhcp6c_max_outstanding': {
                    },
                    'dhcp6c_duid_type': {
                    },
                    'dhcp6c_ia_type': {
                    },
                    'dhcp6c_req_opts_config': {
                    },
                    'dhcp6c_tout_and_retr_config': {
                    },
                    'dhcp6c_renew_timer': {
                    },
                    'dhcp6c_ia_t2': {
                    },
                    'id': {
                    },
                    'dhcp6c_ia_t1': {
                    },
                    'dhcp6c_initial_srate': {
                    }
                }]
            },
            'createdOn': {
            },
            'contentType': {
            },
            'revision': {
            },
            'operations': {
                'importNetwork': [{
                }],
                'list': [{
                }],
                'search': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'delete': [{
                }]
            }
        },
        'topology': {
            'ixoslicensed': {
            },
            'ixos': {
            },
            'cnState': [{
                'cnSlotNo': {
                },
                'licensed': {
                },
                'cnName': {
                },
                'firmwareUpgrade': {
                },
                'cnSerial': {
                },
                'cnId': {
                },
                'marketingName': {
                }
            }],
            'runningTest': [{
                'phase': {
                },
                'reservedEngines': [{
                }],
                'timeRemaining': {
                },
                'runtime': {
                },
                'label': {
                },
                'completed': {
                },
                'initProgress': {
                },
                'result': {
                },
                'port': [{
                }],
                'capturing': {
                },
                'progress': {
                },
                'testid': {
                    'host': {
                    },
                    'name': {
                    },
                    'iteration': {
                    }
                },
                'state': {
                },
                'user': {
                },
                'currentTest': {
                }
            }],
            'model': {
            },
            'slot': [{
                'port': [{
                    'owner': {
                    },
                    'note': {
                    },
                    'auto': {
                    },
                    'link': {
                    },
                    'media': {
                    },
                    'speed': {
                    },
                    'mtu': {
                    },
                    'currentMode': {
                    },
                    'number': {
                    },
                    'exportProgress': {
                    },
                    'ifmacaddr': {
                    },
                    'ifname': {
                    },
                    'reservedBy': {
                    },
                    'capturing': {
                    },
                    'model': {
                    },
                    'id': {
                    },
                    'state': {
                    },
                    'possibleModes': {
                    },
                    'group': {
                    }
                }],
                'np': [{
                    'note': {
                    },
                    'cnId': {
                    },
                    'reservedBy': {
                    },
                    'name': {
                    },
                    'id': {
                    },
                    'state': {
                    },
                    'group': {
                    },
                    'resourceType': {
                    }
                }],
                'mode': {
                },
                'fpga': [{
                    'note': {
                    },
                    'reservedBy': {
                    },
                    'name': {
                    },
                    'id': {
                    },
                    'state': {
                    },
                    'group': {
                    },
                    'resourceType': {
                    }
                }],
                'firmwareUpgrade': {
                },
                'model': {
                },
                'state': {
                },
                'id': {
                },
                'serialNumber': {
                }
            }],
            'serialNumber': {
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
            'operations': {
                'stopRun': [{
                }],
                'getPortAvailableModes': [{
                    'modes': [{
                        'name': {
                        },
                        'fanoutId': {
                        }
                    }],
                    'slot': {
                    },
                    'port': {
                    }
                }],
                'reserveResources': [{
                }],
                'exportCapture': [{
                }],
                'addPortNote': [{
                }],
                'addResourceNote': [{
                }],
                'reserveAllCnResources': [{
                }],
                'setCardMode': [{
                }],
                'setCardSpeed': [{
                }],
                'setCardFanout': [{
                }],
                'setPerfAcc': [{
                }],
                'releaseResources': [{
                }],
                'reboot': [{
                }],
                'releaseResource': [{
                }],
                'setPortSettings': [{
                }],
                'run': [{
                }],
                'getFanoutModes': [{
                    'cardModel': {
                    },
                    'fanout': [{
                        'name': {
                        },
                        'fanoutId': {
                        }
                    }]
                }],
                'unreserve': [{
                }],
                'rebootComputeNode': [{
                }],
                'reserve': [{
                }],
                'softReboot': [{
                }],
                'reserveResource': [{
                }],
                'releaseAllCnResources': [{
                }],
                'setPortFanoutMode': [{
                }]
            }
        },
        'evasionProfile': {
            'lockedBy': {
            },
            'createdBy': {
            },
            'author': {
            },
            'name': {
            },
            'description': {
            },
            'label': {
            },
            'StrikeOptions': {
                'TCP': {
                    'DuplicateBadSyn': {
                    },
                    'DuplicateBadChecksum': {
                    },
                    'SneakAckHandshake': {
                    },
                    'AcknowledgeAllSegments': {
                    },
                    'DuplicateBadSeq': {
                    },
                    'SkipHandshake': {
                    },
                    'SourcePort': {
                    },
                    'MaxSegmentSize': {
                    },
                    'DestinationPort': {
                    },
                    'DuplicateBadReset': {
                    },
                    'DestinationPortType': {
                    },
                    'DuplicateLastSegment': {
                    },
                    'DuplicateNullFlags': {
                    },
                    'SegmentOrder': {
                    },
                    'SourcePortType': {
                    }
                },
                'JAVASCRIPT': {
                    'Obfuscate': {
                    },
                    'Encoding': {
                    }
                },
                'FTP': {
                    'PadCommandWhitespace': {
                    },
                    'Username': {
                    },
                    'FTPEvasionLevel': {
                    },
                    'AuthenticationType': {
                    },
                    'Password': {
                    }
                },
                'IPv6': {
                    'TC': {
                    }
                },
                'DCERPC': {
                    'MultiContextBindHead': {
                    },
                    'MultiContextBind': {
                    },
                    'MultiContextBindTail': {
                    },
                    'MaxFragmentSize': {
                    },
                    'UseObjectID': {
                    }
                },
                'RTF': {
                    'FictitiousCW': {
                    },
                    'ASCII_Escaping': {
                    },
                    'MixedCase': {
                    },
                    'WhiteSpace': {
                    }
                },
                'POP3': {
                    'PadCommandWhitespace': {
                    },
                    'Username': {
                    },
                    'POP3UseProxyMode': {
                    },
                    'AuthenticationType': {
                    },
                    'Password': {
                    }
                },
                'Variations': {
                    'Subset': {
                    },
                    'Shuffle': {
                    },
                    'VariantTesting': {
                    },
                    'Limit': {
                    },
                    'TestType': {
                    }
                },
                'OLE': {
                    'RefragmentData': {
                    }
                },
                'HTML': {
                    'HTMLUnicodeUTF8EncodingMode': {
                    },
                    'HTMLUnicodeUTF8EncodingSize': {
                    },
                    'HTMLUnicodeEncoding': {
                    },
                    'HTMLUnicodeUTF7EncodingMode': {
                    }
                },
                'EMAIL': {
                    'EnvelopeType': {
                    },
                    'ShuffleHeaders': {
                    },
                    'To': {
                    },
                    'From': {
                    }
                },
                'Global': {
                    'FalsePositives': {
                    },
                    'IOTimeout': {
                    },
                    'AllowDeprecated': {
                    },
                    'BehaviorOnTimeout': {
                    },
                    'MaxTimeoutPerStrike': {
                    },
                    'CachePoisoning': {
                    }
                },
                'MS_Exchange_Ports': {
                    'SystemAttendant': {
                    }
                },
                'PDF': {
                    'HexEncodeNames': {
                    },
                    'ShortFilterNames': {
                    },
                    'RandomizeDictKeyOrder': {
                    },
                    'Version': {
                    },
                    'PreHeaderData': {
                    }
                },
                'SNMP': {
                    'CommunityString': {
                    }
                },
                'COMMAND': {
                    'PadCommandWhitespace': {
                    },
                    'PadPathSlashes': {
                    },
                    'Malicious': {
                    }
                },
                'ICMP': {
                    'DoEcho': {
                    }
                },
                'UDP': {
                    'DestinationPortType': {
                    },
                    'SourcePort': {
                    },
                    'SourcePortType': {
                    },
                    'DestinationPort': {
                    }
                },
                'IP': {
                    'ReadWriteWindowSize': {
                    },
                    'RFC3128FakePort': {
                    },
                    'FragEvasion': {
                    },
                    'RFC3128': {
                    },
                    'TTL': {
                    },
                    'MaxReadSize': {
                    },
                    'RFC3514': {
                    },
                    'FragPolicy': {
                    },
                    'MaxFragSize': {
                    },
                    'FragOrder': {
                    },
                    'TOS': {
                    },
                    'IPEvasionsOnBothSides': {
                    },
                    'MaxWriteSize': {
                    }
                },
                'SMB': {
                    'Username': {
                    },
                    'RandomPipeOffset': {
                    },
                    'MaxReadSize': {
                    },
                    'MaxWriteSize': {
                    },
                    'AuthenticationType': {
                    },
                    'Password': {
                    }
                },
                'IMAP4': {
                    'Username': {
                    },
                    'IMAPUseProxyMode': {
                    },
                    'AuthenticationType': {
                    },
                    'Password': {
                    }
                },
                'HTTP': {
                    'ClientChunkedTransferSize': {
                    },
                    'EncodeUnicodeBareByte': {
                    },
                    'VirtualHostname': {
                    },
                    'EncodeUnicodePercentU': {
                    },
                    'GetParameterRandomPrepend': {
                    },
                    'EncodeSecondNibbleHex': {
                    },
                    'EncodeUnicodeInvalid': {
                    },
                    'ServerChunkedTransferSize': {
                    },
                    'VersionRandomizeCase': {
                    },
                    'URIRandomizeCase': {
                    },
                    'AuthenticationType': {
                    },
                    'ServerCompression': {
                    },
                    'VirtualHostnameType': {
                    },
                    'URIPrependAltSpaces': {
                    },
                    'URIPrependAltSpacesSize': {
                    },
                    'EncodeFirstNibbleHex': {
                    },
                    'MethodRandomInvalid': {
                    },
                    'VersionRandomInvalid': {
                    },
                    'ServerChunkedTransfer': {
                    },
                    'EncodeDoublePercentHex': {
                    },
                    'URIAppendAltSpacesSize': {
                    },
                    'EncodeHexRandom': {
                    },
                    'DirectorySelfReference': {
                    },
                    'EndRequestFakeHTTPHeader': {
                    },
                    'EncodeUnicodeAll': {
                    },
                    'EncodeUnicodeRandom': {
                    },
                    'Base64EncodePOSTData': {
                    },
                    'IgnoreHeaders': {
                    },
                    'RequestFullURL': {
                    },
                    'HTTPTransportMethods': {
                    },
                    'Password': {
                    },
                    'MethodRandomizeCase': {
                    },
                    'MethodURISpaces': {
                    },
                    'ShuffleHeaders': {
                    },
                    'DirectoryFakeRelative': {
                    },
                    'URIAppendAltSpaces': {
                    },
                    'MethodURITabs': {
                    },
                    'RequireLeadingSlash': {
                    },
                    'EncodeDoubleNibbleHex': {
                    },
                    'ForwardToBackSlashes': {
                    },
                    'PadHTTPPost': {
                    },
                    'MethodURINull': {
                    },
                    'Username': {
                    },
                    'VersionUse0_9': {
                    },
                    'EncodeHexAll': {
                    },
                    'PostParameterRandomPrepend': {
                    },
                    'ClientChunkedTransfer': {
                    },
                    'HTTPServerProfile': {
                    }
                },
                'SELF': {
                    'ApplicationPings': {
                    },
                    'TraversalVirtualDirectory': {
                    },
                    'AppSimUseNewTuple': {
                    },
                    'StartingFuzzerOffset': {
                    },
                    'URI': {
                    },
                    'FileTransferRandCase': {
                    },
                    'UnicodeTraversalWindowsDirectory': {
                    },
                    'AREA-ID': {
                    },
                    'AppSimAppProfile': {
                    },
                    'Repetitions': {
                    },
                    'FileTransferExtension': {
                    },
                    'Password': {
                    },
                    'AppSimSmartflow': {
                    },
                    'HTMLPadding': {
                    },
                    'MaximumIterations': {
                    },
                    'FileTransferFile': {
                    },
                    'AS-ID': {
                    },
                    'AppSimSuperflow': {
                    },
                    'EndingFuzzerOffset': {
                    },
                    'ReportCLSIDs': {
                    },
                    'DelaySeconds': {
                    },
                    'Username': {
                    },
                    'UnicodeTraversalVirtualDirectory': {
                    },
                    'TraversalWindowsDirectory': {
                    },
                    'FileTransferName': {
                    },
                    'MaximumRuntime': {
                    },
                    'ROUTER-ID': {
                    },
                    'TraversalRequestFilename': {
                    }
                },
                'SHELLCODE': {
                    'RandomNops': {
                    }
                },
                'SSL': {
                    'ClientCertificateFile': {
                    },
                    'EnableOnAllTCP': {
                    },
                    'SecurityProtocol': {
                    },
                    'DestPortOverride': {
                    },
                    'ServerCertificateFile': {
                    },
                    'ServerKeyFile': {
                    },
                    'EnableOnAllHTTP': {
                    },
                    'ClientKeyFile': {
                    },
                    'Cipher': {
                    },
                    'DisableDefaultStrikeSSL': {
                    }
                },
                'SUNRPC': {
                    'OneFragmentMultipleTCPSegmentsCount': {
                    },
                    'RPCFragmentTCPSegmentDistribution': {
                    },
                    'TCPFragmentSize': {
                    },
                    'NullCredentialPadding': {
                    }
                },
                'FILETRANSFER': {
                    'SmtpEncoding': {
                    },
                    'CompressionMethod': {
                    },
                    'FtpTransferMethod': {
                    },
                    'TransportProtocol': {
                    },
                    'Imap4Encoding': {
                    },
                    'Pop3Encoding': {
                    }
                },
                'UNIX': {
                    'PadCommandWhitespace': {
                    },
                    'PadPathSlashes': {
                    }
                },
                'SMTP': {
                    'SMTPUseProxyMode': {
                    },
                    'PadCommandWhitespace': {
                    },
                    'ShuffleHeaders': {
                    }
                },
                'Ethernet': {
                    'MTU': {
                    }
                },
                'MALWARE': {
                    'FilenameInsertEnvVar': {
                    },
                    'SmtpEncoding': {
                    },
                    'CompressionMethod': {
                    },
                    'FtpTransferMethod': {
                    },
                    'TransportProtocol': {
                    },
                    'Imap4Encoding': {
                    },
                    'Pop3Encoding': {
                    }
                },
                'SIP': {
                    'EnvelopeType': {
                    },
                    'CompactHeaders': {
                    },
                    'PadHeadersWhitespace': {
                    },
                    'RandomizeCase': {
                    },
                    'ShuffleHeaders': {
                    },
                    'To': {
                    },
                    'From': {
                    },
                    'PadHeadersLineBreak': {
                    }
                },
                'operations': {
                    'getStrikeOptions': [{
                        'name': {
                        },
                        'description': {
                        },
                        'realtimeGroup': {
                        },
                        'label': {
                        },
                        'units': {
                        }
                    }]
                }
            },
            'createdOn': {
            },
            'contentType': {
            },
            'revision': {
            },
            'operations': {
                'search': [{
                }],
                'delete': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'load': [{
                }],
                'new': [{
                }]
            }
        },
        'strikes': {
            'severity': {
            },
            'year': {
            },
            'variants': {
            },
            'reference': [{
                'label': {
                },
                'type': {
                },
                'value': {
                }
            }],
            'path': {
            },
            'protocol': {
            },
            'fileSize': {
            },
            'fileExtension': {
            },
            'name': {
            },
            'id': {
            },
            'category': {
            },
            'keyword': [{
                'name': {
                }
            }],
            'direction': {
            },
            'operations': {
                'search': [{
                }]
            }
        },
        'reports': {
            'endtime': {
            },
            'starttime': {
            },
            'label': {
            },
            'testname': {
            },
            'network': {
            },
            'duration': {
            },
            'result': {
            },
            'size': {
            },
            'isPartOfResiliency': {
            },
            'name': {
            },
            'iteration': {
            },
            'testid': {
                'host': {
                },
                'name': {
                },
                'iteration': {
                }
            },
            'user': {
            },
            'operations': {
                'exportReport': [{
                }],
                'delete': [{
                }],
                'search': [{
                }],
                'getReportContents': [{
                }],
                'getReportTable': [{
                }]
            }
        },
        'statistics': {
            'component': [{
                'statNames': [{
                    'name': {
                    },
                    'description': {
                    },
                    'realtimeGroup': {
                    },
                    'label': {
                    },
                    'units': {
                    }
                }],
                'label': {
                }
            }]
        },
        'results': [{
            'name': {
            },
            'content': {
            },
            'datasetvals': {
            },
            'operations': {
                'getHistoricalResultSize': [{
                }],
                'getHistoricalSeries': [{
                }],
                'getGroups': [{
                    'lockedBy': {
                    },
                    'createdBy': {
                    },
                    'author': {
                    },
                    'description': {
                    },
                    'label': {
                    },
                    'createdOn': {
                    },
                    'contentType': {
                    },
                    'revision': {
                    }
                }]
            }
        }]
    }

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

    def __call__(cls, *args, **kwds):
        return DataModelMeta._decorate_model_object(type.__call__(cls, *args, **kwds))

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

    def __full_path__(self):
        return '%s/%s' % (self._path, self._name)

    def __data_model_path__(self):
        return '%s/%s' % (self._model_path, self._name)

    def __url__(self):
        return 'https://%s/bps/api/v2/core%s' % (self._wrapper.host, self.__full_path__())

    def __repr__(self):
        return 'proxy object for \'%s\' ' % (self.__url__())

    def __getitem__(self, item):
        return self._getitem_(item)

    def get(self, responseDepth=None, **kwargs):
        return self._wrapper._get(self._path+'/'+self._name, responseDepth, **kwargs)

    def __cached_get__(self, field):
        if field not in self.__cache: self.__cache[field] = self._wrapper._get(self.__data_model_path__()+"/"+field)
        return self.__cache[field]

    def patch(self, value):
        return self._wrapper._patch(self._path+'/'+self._name, value)

    def set(self, value):
        return self.patch(value)

    def put(self, value):
        return self._wrapper._put(self._path+'/'+self._name, value)

    def delete(self):
        return self._wrapper._delete(self._path+'/'+self._name)

    def help(self):
        doc_data = self._wrapper._options(self._path+'/'+self._name)
        if doc_data and 'custom' in doc_data:
            doc_data = doc_data['custom']
        if doc_data and 'description' in doc_data:
            print(doc_data['description'])
