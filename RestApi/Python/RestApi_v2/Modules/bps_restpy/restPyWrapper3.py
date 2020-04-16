"""
# MIT LICENSE
#
# Copyright 1997 - 2019 by IXIA Keysight
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE. 
*Created with Breaking Point build :  9.00v9.00.108.12"""
import requests
import json
import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=1).pprint


class TlsAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block)

### this BPS REST API wrapper is generated for version: 9.00.0.182
class BPS(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.sessionId = None
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter())
        self.administration = DataModelProxy(wrapper=self, name='administration')
        self.strikes = DataModelProxy(wrapper=self, name='strikes')
        self.statistics = DataModelProxy(wrapper=self, name='statistics')
        self.strikeList = DataModelProxy(wrapper=self, name='strikeList')
        self.loadProfile = DataModelProxy(wrapper=self, name='loadProfile')
        self.testmodel = DataModelProxy(wrapper=self, name='testmodel')
        self.evasionProfile = DataModelProxy(wrapper=self, name='evasionProfile')
        self.topology = DataModelProxy(wrapper=self, name='topology')
        self.superflow = DataModelProxy(wrapper=self, name='superflow')
        self.network = DataModelProxy(wrapper=self, name='network')
        self.appProfile = DataModelProxy(wrapper=self, name='appProfile')
        self.results = DataModelProxy(wrapper=self, name='results')
        self.reports = DataModelProxy(wrapper=self, name='reports')
        self.capture = DataModelProxy(wrapper=self, name='capture')

    ### connect to the system
    def __connect(self):
        r = self.session.post(url='https://' + self.host + '/bps/api/v1/auth/session', data=json.dumps({'username': self.user, 'password': self.password}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            self.sessionId = r.json().get('sessionId')
            self.session.headers['sessionId'] = r.json().get('sessionId')
            self.session.headers['X-API-KEY'] = r.json().get('apiKey')
            print('Successfully connected to %s.' % self.host)
        else:
            raise Exception('Failed connecting to %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### disconnect from the system
    def __disconnect(self):
        r = self.session.delete(url='https://' + self.host + '/api/v1/auth/session', verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 204):
            self.sessionId = None
            if 'sessionId' in self.session.headers:
                del self.session.headers['sessionId']
                del self.session.headers['X-API-KEY']
            print('Successfully disconnected from %s.' % self.host)
        else:
            raise Exception('Failed disconnecting from %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### login into the bps system
    def login(self):
        self.__connect()
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/login', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            print('Login successful.\nWelcome %s. \nYour session id is %s' % (self.user, self.sessionId))
        else:
            raise Exception('Login failed.\ncode:%s, content:%s' % (r.status_code, r.content))

    ### logout from the bps system
    def logout(self):
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/logout', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            print('Logout successful. \nBye %s.' % self.user)
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
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code in [200, 204]):
            return json.loads(r.content) if jsonContent else r.content
        raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### Get from data model
    def _patch(self, path, value):
        r = self.session.patch(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### Get from data model
    def _put(self, path, value):
        r = self.session.put(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code != 204):
            raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### Get from data model
    def _delete(self, path):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/'+ path
        headers = {'content-type': 'application/json'}
        r = self.session.delete(url=requestUrl, headers=headers, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code in [200, 204]):
            return json.loads(r.content) if jsonContent else r.content
        raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### OPTIONS request
    def _options(self, path):
        r = self.session.options('https://' + self.host + '/bps/api/v2/core/'+ path)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code in [200]):
            return json.loads(r.content) if jsonContent else r.content
        raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### generic post operation
    def _post(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        r = self.session.post(url=requestUrl, headers={'content-type': 'application/json'}, data=json.dumps(kwargs), verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code in [200, 204, 202]):
            return json.loads(r.content) if jsonContent else r.content
        raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### generic import operation
    def _import(self, path, filename, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        files = {'file': (kwargs['name'], open(filename, 'rb'), 'application/xml')}
        r = self.session.post(url=requestUrl, files=files, data={'fileInfo':str(kwargs)}, verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code in [200, 204]):
            return json.loads(r.content) if jsonContent else r.content
        raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

    ### generic post operation
    def _export(self, path, **kwargs):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/' + path
        r = self.session.post(url=requestUrl, headers={'content-type': 'application/json'}, data=json.dumps(kwargs), verify=False)
        if(r.status_code == 400):
            methodCall = '%s'%path.replace('/', '.').replace('.operations', '')
            content_message = r.content.decode() + ' Execute: help(<BPS session name>%s) for more information about the method.'%methodCall
            raise Exception({'status_code': r.status_code, 'content': content_message})
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
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
            raise Exception({'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content})

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
        return self._wrapper._post('/results/' + self._name + '/operations/getHistoricalSeries', **{'runid': runid, 'componentid': componentid, 'dataindex': dataindex, 'group': group})

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
        return self._wrapper._post('/superflow/actions/' + self._name + '/operations/getActionInfo', **{'id': id})

    ### Deletes a given Application Profile from the database.
    @staticmethod
    def _appProfile_operations_delete(self, name):
        """
        Deletes a given Application Profile from the database.
        :param name (string): The name of the Application Profiles.
        """
        return self._wrapper._post('/appProfile/operations/delete', **{'name': name})

    ### null
    @staticmethod
    def _reports_operations_exportReport(self, filepath, runid, reportType, sectionIds='', dataType='ALL'):
        """
        :param filepath (string): The local path where to export the report, including the report name.
        :param runid (number): Test RUN ID
        :param reportType (string): Report file format to be exported in.
        :param sectionIds (string): Chapter Ids. Can be extracted a chapter or many, a sub-chapter or many or the entire report: (sectionIds='6' / sectionIds='5,6,7' / sectionIds='7.4,8.5.2,8.6.3.1' / sectionIds=''(to export the entire report))
        :param dataType (string): Report content data type to export. Default value is 'all data'. For tabular only use 'TABLE' and for graphs only use 'CHARTS'.
        """
        return self._wrapper._export('/reports/operations/exportReport', **{'filepath': filepath, 'runid': runid, 'reportType': reportType, 'sectionIds': sectionIds, 'dataType': dataType})

    ### null
    @staticmethod
    def _strikeList_operations_exportStrikeList(self, name, filepath):
        """
        :param name (string): The name of the strike list to be exported.
        :param filepath (string): The local path where to save the exported object. The file should have .bap extension
        """
        return self._wrapper._export('/strikeList/operations/exportStrikeList', **{'name': name, 'filepath': filepath})

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

    ### Exports a port capture from a test run
    @staticmethod
    def _topology_operations_exportCapture(self, filepath, args):
        """
        Exports a port capture from a test run
        :param filepath (string): The local path where to save the exported object.
        :param args (object): Export filters. The Possible values for: 'dir'(direction) are 'tx','rx','both';for 'sizetype' and 'starttype'(units for size and start) are 'megabytes' or 'frames'
               object of object with fields
                      port (number): Port number
                      slot (number): Slot number
                      dir (string): Capturing direction (rx, tx, both)
                      size (number): The size of the capture to be exported.
                      start (number): Start at point.
                      sizetype (string): The size unit: megabytes or frames.
                      starttype (string): The start unit: megabytes or frames.
        """
        return self._wrapper._export('/topology/operations/exportCapture', **{'filepath': filepath, 'args': args})

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

    ### Recompute percentages in the current working Application Profile
    @staticmethod
    def _appProfile_operations_recompute(self):
        """
        Recompute percentages in the current working Application Profile
        """
        return self._wrapper._post('/appProfile/operations/recompute', **{})

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

    ### Imports a test model, given as a file.
    @staticmethod
    def _testmodel_operations_importModel(self, name, filename, force):
        """
        Imports a test model, given as a file.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/testmodel/operations/importModel', **{'name': name, 'filename': filename, 'force': force})

    ### Imports an application profile, given as a file.
    @staticmethod
    def _appProfile_operations_importAppProfile(self, name, filename, force):
        """
        Imports an application profile, given as a file.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/appProfile/operations/importAppProfile', **{'name': name, 'filename': filename, 'force': force})

    ### Imports a network neighborhood model, given as a file.
    @staticmethod
    def _network_operations_importNetwork(self, name, filename, force):
        """
        Imports a network neighborhood model, given as a file.
        :param name (string): The name of the object being imported
        :param filename (string): The file containing the object
        :param force (bool): Force to import the file and replace the object having the same name.
        """
        return self._wrapper._import('/network/operations/importNetwork', **{'name': name, 'filename': filename, 'force': force})

    ### Removes an action from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeAction(self, id):
        """
        Removes an action from the current working SuperFlow.
        :param id (number): The action ID.
        """
        return self._wrapper._post('/superflow/operations/removeAction', **{'id': id})

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

    ### Retrieves the real time statistics for the running test, by giving the run id.
    @staticmethod
    def _testmodel_operations_realTimeStats(self, runid, rtsgroup, numSeconds, numDataPoints=1):
        """
        Retrieves the real time statistics for the running test, by giving the run id.
        :param runid (number): Test RUN ID
        :param rtsgroup (string): Real Time Stats group name. Values for this can be get from 'statistics' node, inside 'statNames' from each component at 'realtime Group' key/column. Examples: l7STats, all, bpslite, summary, clientStats etc.
        :param numSeconds (number): The number of seconds.  If negative, means from the end
        :param numDataPoints (number): The number of data points, the default is 1.
        :return result (object): 
               object of object with fields
                      testStuck (bool): 
                      time (number): 
                      progress (number): 
                      values (string): 
        """
        return self._wrapper._post('/testmodel/operations/realTimeStats', **{'runid': runid, 'rtsgroup': rtsgroup, 'numSeconds': numSeconds, 'numDataPoints': numDataPoints})

    ### null
    @staticmethod
    def _topology_operations_reserve(self, reservation, force=False):
        """
        :param reservation (list): 
               list of object with fields
                      group (number): 
                      slot (number): 
                      port (number): 
                      capture (bool): 
        :param force (bool): 
        """
        return self._wrapper._post('/topology/operations/reserve', **{'reservation': reservation, 'force': force})

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
        return self._wrapper._post('/testmodel/component/' + self._name + '/operations/getComponentPresetNames', **{'type': type})

    ### Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
    @staticmethod
    def _strikeList_operations_add(self, strike):
        """
        Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
        :param strike (list): The list of strikes to add.
               list of object with fields
                      id (string): Strike path.
        """
        return self._wrapper._post('/strikeList/operations/add', **{'strike': strike})

    ### Adds a note to given port.
    @staticmethod
    def _topology_operations_addPortNote(self, interface, note):
        """
        Adds a note to given port.
        :param interface (object): Slot and Port ID.
               object of object with fields
                      slot (number): 
                      port (number): 
        :param note (string): Note info.
        """
        return self._wrapper._post('/topology/operations/addPortNote', **{'interface': interface, 'note': note})

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
        return self._wrapper._post('/superflow/flows/' + self._name + '/operations/getCannedFlows', **{})

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
    def _superflow_actions_operations_getActionChoices(self, id):
        """
        :param id (number): the flow id
        """
        return self._wrapper._post('/superflow/actions/' + self._name + '/operations/getActionChoices', **{'id': id})

    ### null
    @staticmethod
    def _superflow_flows_operations_getFlowChoices(self, id, name):
        """
        :param id (number): The flow id.
        :param name (string): The flow type/name.
        :return result (list): 
        """
        return self._wrapper._post('/superflow/flows/' + self._name + '/operations/getFlowChoices', **{'id': id, 'name': name})

    ### Deletes a Test Report from the database.
    @staticmethod
    def _reports_operations_delete(self, runid):
        """
        Deletes a Test Report from the database.
        :param runid (number): The test run id that generated the report you want to delete.
        """
        return self._wrapper._post('/reports/operations/delete', **{'runid': runid})

    ### Retrieves all the security options
    @staticmethod
    def _evasionProfile_StrikeOptions_operations_getStrikeOptions(self):
        """
        Retrieves all the security options
        :return result (list): 
        """
        return self._wrapper._post('/evasionProfile/StrikeOptions/operations/getStrikeOptions', **{})

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

    ### Exports everything including test models, network configurations and others from system.
    @staticmethod
    def _administration_operations_exportAllTests(self, filepath):
        """
        Exports everything including test models, network configurations and others from system.
        :param filepath (string): The local path where to save the compressed file with all the models. The path must contain the file name and extension (.tar.gz): '/d/c/f/AllTests.tar.gz'
        """
        return self._wrapper._export('/administration/operations/exportAllTests', **{'filepath': filepath})

    ### Exports an Application profile and all of its dependencies.
    @staticmethod
    def _appProfile_operations_exportAppProfile(self, name, attachments, filepath):
        """
        Exports an Application profile and all of its dependencies.
        :param name (string): The name of the test model to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        """
        return self._wrapper._export('/appProfile/operations/exportAppProfile', **{'name': name, 'attachments': attachments, 'filepath': filepath})

    ### Deletes a given Super Flow from the database.
    @staticmethod
    def _superflow_operations_delete(self, name):
        """
        Deletes a given Super Flow from the database.
        :param name (string): The name of the Super Flow.
        """
        return self._wrapper._post('/superflow/operations/delete', **{'name': name})

    ### Deletes a given Test Model from the database.
    @staticmethod
    def _testmodel_operations_delete(self, name):
        """
        Deletes a given Test Model from the database.
        :param name (string): The name of the Test Model.
        """
        return self._wrapper._post('/testmodel/operations/delete', **{'name': name})

    ### Removes a flow from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeFlow(self, id):
        """
        Removes a flow from the current working SuperFlow.
        :param id (number): The flow ID.
        """
        return self._wrapper._post('/superflow/operations/removeFlow', **{'id': id})

    ### null
    @staticmethod
    def _loadProfile_operations_load(self, template):
        """
        :param template (string): 
        """
        return self._wrapper._post('/loadProfile/operations/load', **{'template': template})

    ### null
    @staticmethod
    def _administration_license_operations_import(self, filename, server):
        """
        :param filename (string): import file path
        :param server (string): server
        """
        return self._wrapper._import('/administration/license/operations/import', **{'filename': filename, 'server': server})

    ### null
    @staticmethod
    def _capture_operations_importCapture(self, name, filename, force):
        """
        :param name (string): The name of the capture being imported
        :param filename (string): The file containing the capture object
        :param force (bool): Force to import the file and the object having the same name will be replaced.
        """
        return self._wrapper._import('/capture/operations/importCapture', **{'name': name, 'filename': filename, 'force': force})

    ### Exports a wanted test model by giving its name or its test run id.
    @staticmethod
    def _testmodel_operations_exportModel(self, name, attachments, filepath, runid=None):
        """
        Exports a wanted test model by giving its name or its test run id.
        :param name (string): The name of the test model to be exported.
        :param attachments (bool): True if object attachments are needed.
        :param filepath (string): The local path where to save the exported object.
        :param runid (number): Test RUN ID
        """
        return self._wrapper._export('/testmodel/operations/exportModel', **{'name': name, 'attachments': attachments, 'filepath': filepath, 'runid': runid})

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

    ### Deletes a specified load profile from the database.
    @staticmethod
    def _loadProfile_operations_delete(self, name):
        """
        Deletes a specified load profile from the database.
        :param name (string): The name of the loadProfile object to delete.
        """
        return self._wrapper._post('/loadProfile/operations/delete', **{'name': name})

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

    ### null
    @staticmethod
    def _results_operations_getHistoricalResultSize(self, runid, componentid, group):
        """
        :param runid (number): The test run id
        :param componentid (string): The component identifier
        :param group (string): The data group or one of the BPS component main groups. The group name can be get by executing the operation 'getGroups' from results node
        :return result (string): 
        """
        return self._wrapper._post('/results/' + self._name + '/operations/getHistoricalResultSize', **{'runid': runid, 'componentid': componentid, 'group': group})

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

    ### Reboots the card. Only available for PerfectStorm and CloudStorm cards.
    @staticmethod
    def _topology_operations_reboot(self, board):
        """
        Reboots the card. Only available for PerfectStorm and CloudStorm cards.
        :param board (number): 
        """
        return self._wrapper._post('/topology/operations/reboot', **{'board': board})

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
        return self._wrapper._post('/results/' + self._name + '/operations/getGroups', **{'name': name, 'dynamicEnums': dynamicEnums, 'includeOutputs': includeOutputs})

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

    ### Deletes a given Strike List from the database.
    @staticmethod
    def _strikeList_operations_delete(self, name):
        """
        Deletes a given Strike List from the database.
        :param name (string): The name of the Strike List to be deleted.
        """
        return self._wrapper._post('/strikeList/operations/delete', **{'name': name})

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
    def _strikeList_operations_search(self, searchString='', limit=10, sort='name', sortorder='ascending'):
        """
        :param searchString (string): Search strike list name matching the string given.
        :param limit (number): The limit of rows to return
        :param sort (string): Parameter to sort by. Default is by name.
        :param sortorder (string): The sort order (ascending/descending). Default is ascending.
        """
        return self._wrapper._post('/strikeList/operations/search', **{'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder})

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

    ### Removes a component from the current working Test Model.
    @staticmethod
    def _testmodel_operations_remove(self, id):
        """
        Removes a component from the current working Test Model.
        :param id (string): The component id.
        """
        return self._wrapper._post('/testmodel/operations/remove', **{'id': id})

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

    ### Deletes a given Evasion Profile from the database.
    @staticmethod
    def _evasionProfile_operations_delete(self, name):
        """
        Deletes a given Evasion Profile from the database.
        :param name (string): The name of the profile to delete.
        """
        return self._wrapper._post('/evasionProfile/operations/delete', **{'name': name})

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

    ### Sets a User Preference.
    @staticmethod
    def _administration_userSettings_operations_changeUserSetting(self, name, value):
        """
        Sets a User Preference.
        :param name (string): The setting name.
        :param value (string): The new value for setting.
        """
        return self._wrapper._post('/administration/userSettings/' + self._name + '/operations/changeUserSetting', **{'name': name, 'value': value})

class DataModelMeta(type):
    _dataModel = {
        'administration': {
            'license': {
                'servers': [{
                    'id': {
                    },
                    'hostId': {
                    }
                }],
                'version': {
                },
                'installed': {
                    'server': {
                    },
                    'license': [{
                        'product': {
                        },
                        'maintenanceExpiry': {
                        },
                        'description': {
                        },
                        'quantity': {
                        },
                        'activationId': {
                        },
                        'licenseExpiry': {
                        }
                    }]
                },
                'operations': {
                    'import': [{
                    }]
                }
            },
            'userSettings': [{
                'content': {
                },
                'name': {
                },
                'operations': {
                    'changeUserSetting': [{
                    }]
                }
            }],
            'systemSettings': {
                'createdOn': {
                },
                'author': {
                },
                'revision': {
                },
                'createdBy': {
                },
                'lockedBy': {
                },
                'description': {
                },
                'guardrailSettings': {
                    'testStartPrevention': {
                    },
                    'testStatusWarning': {
                    },
                    'enableStrictMode': {
                    },
                    'testStop': {
                    },
                    'stopOnLinkdown': {
                    }
                },
                'strikepackUpdate': {
                    'username': {
                    },
                    'check': {
                    },
                    'interval': {
                    },
                    'password': {
                    }
                },
                'label': {
                },
                'softwareUpdate': {
                    'username': {
                    },
                    'check': {
                    },
                    'interval': {
                    },
                    'password': {
                    }
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
                'contentType': {
                }
            },
            'operations': {
                'logs': [{
                }],
                'exportAllTests': [{
                }]
            }
        },
        'strikes': {
            'fileExtension': {
            },
            'protocol': {
            },
            'direction': {
            },
            'keyword': [{
                'name': {
                }
            }],
            'severity': {
            },
            'reference': [{
                'value': {
                },
                'label': {
                },
                'type': {
                }
            }],
            'id': {
            },
            'fileSize': {
            },
            'category': {
            },
            'name': {
            },
            'path': {
            },
            'variants': {
            },
            'year': {
            },
            'operations': {
                'search': [{
                }]
            }
        },
        'statistics': {
            'component': [{
                'type': {
                },
                'label': {
                },
                'statNames': [{
                    'choice': [{
                        'description': {
                        },
                        'name': {
                        },
                        'label': {
                        }
                    }],
                    'description': {
                    },
                    'name': {
                    },
                    'label': {
                    },
                    'realtimeGroup': {
                    },
                    'units': {
                    }
                }]
            }]
        },
        'strikeList': {
            'strikes': [{
                'fileExtension': {
                },
                'protocol': {
                },
                'direction': {
                },
                'keyword': [{
                    'name': {
                    }
                }],
                'severity': {
                },
                'reference': [{
                    'value': {
                    },
                    'label': {
                    },
                    'type': {
                    }
                }],
                'id': {
                },
                'fileSize': {
                },
                'category': {
                },
                'name': {
                },
                'path': {
                },
                'variants': {
                },
                'year': {
                }
            }],
            'createdOn': {
            },
            'queryString': {
            },
            'author': {
            },
            'revision': {
            },
            'createdBy': {
            },
            'lockedBy': {
            },
            'description': {
            },
            'name': {
            },
            'label': {
            },
            'numStrikes': {
            },
            'contentType': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'exportStrikeList': [{
                }],
                'add': [{
                }],
                'importStrikeList': [{
                }],
                'remove': [{
                }],
                'delete': [{
                }],
                'search': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }]
            }
        },
        'loadProfile': {
            'presets': [{
                'createdOn': {
                },
                'author': {
                },
                'revision': {
                },
                'createdBy': {
                },
                'lockedBy': {
                },
                'description': {
                },
                'name': {
                },
                'label': {
                },
                'regen': {
                },
                'summaryData': {
                    'unknownUdpAppNames': {
                    },
                    'uploadBytesSum': {
                    },
                    'summaryName': {
                    },
                    'magicNumber': {
                    },
                    'phaseDuration': {
                    },
                    'endTime': {
                    },
                    'downloadBytesSum': {
                    },
                    'miniSlotDuration': {
                    },
                    'version': {
                    },
                    'unknownSslAppNames': {
                    },
                    'startTime': {
                    },
                    'unknownTcpAppNames': {
                    },
                    'dynamicAppNames': {
                    },
                    'deviceType': {
                    },
                    'activeFlowsSum': {
                    },
                    'unknownSslSuperflowName': {
                    },
                    'appStat': [{
                    }],
                    'dynamicSuperflowName': {
                    },
                    'basisOfRegeneration': {
                    }
                },
                'phase': [{
                    'duration': {
                    },
                    'rateDist.unit': {
                    },
                    'sessions.maxPerSecond': {
                    },
                    'sessions.max': {
                    },
                    'rateDist.scope': {
                    },
                    'rateDist.type': {
                    },
                    'rampDist.steadyBehavior': {
                    },
                    'rateDist.min': {
                    },
                    'type': {
                    },
                    'phaseId': {
                    }
                }],
                'contentType': {
                }
            }],
            'createdOn': {
            },
            'author': {
            },
            'revision': {
            },
            'createdBy': {
            },
            'lockedBy': {
            },
            'description': {
            },
            'name': {
            },
            'label': {
            },
            'regen': {
            },
            'summaryData': {
                'unknownUdpAppNames': {
                },
                'uploadBytesSum': {
                },
                'summaryName': {
                },
                'magicNumber': {
                },
                'phaseDuration': {
                },
                'endTime': {
                },
                'downloadBytesSum': {
                },
                'miniSlotDuration': {
                },
                'version': {
                },
                'unknownSslAppNames': {
                },
                'startTime': {
                },
                'unknownTcpAppNames': {
                },
                'dynamicAppNames': {
                },
                'deviceType': {
                },
                'activeFlowsSum': {
                },
                'unknownSslSuperflowName': {
                },
                'appStat': [{
                }],
                'dynamicSuperflowName': {
                },
                'basisOfRegeneration': {
                }
            },
            'phase': [{
                'duration': {
                },
                'rateDist.unit': {
                },
                'sessions.maxPerSecond': {
                },
                'sessions.max': {
                },
                'rateDist.scope': {
                },
                'rateDist.type': {
                },
                'rampDist.steadyBehavior': {
                },
                'rateDist.min': {
                },
                'type': {
                },
                'phaseId': {
                }
            }],
            'contentType': {
            },
            'operations': {
                'save': [{
                }],
                'saveAs': [{
                }],
                'load': [{
                }],
                'delete': [{
                }],
                'createNewCustom': [{
                }]
            }
        },
        'testmodel': {
            'testComponentTypesDescription': [{
                'template': {
                },
                'description': {
                },
                'name': {
                },
                'label': {
                },
                'type': {
                }
            }],
            'summaryInfo': {
                'totalUniqueStrikes': {
                },
                'requiredMTU': {
                },
                'totalUniqueSuperflows': {
                },
                'totalSubnets': {
                },
                'totalMacAddresses': {
                }
            },
            'result': {
            },
            'lastrun': {
            },
            'lockedBy': {
            },
            'label': {
            },
            'sharedComponentSettings': {
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
                'maximumConcurrentFlows': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                },
                'maxFlowCreationRate': {
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
                },
                'samplePeriod': {
                    'content': {
                    },
                    'current': {
                    },
                    'original': {
                    }
                }
            },
            'lastrunby': {
            },
            'network': {
            },
            'createdOn': {
            },
            'author': {
            },
            'revision': {
            },
            'duration': {
            },
            'createdBy': {
            },
            'component': [{
                'tags': [{
                    'id': {
                    },
                    'domainId': {
                        'iface': {
                        },
                        'external': {
                        },
                        'name': {
                        }
                    },
                    'type': {
                    }
                }],
                'originalPreset': {
                },
                'lockedBy': {
                },
                'reportResults': {
                },
                'timeline': {
                    'timesegment': [{
                        'label': {
                        },
                        'type': {
                        },
                        'size': {
                        }
                    }]
                },
                'label': {
                },
                '@type:layer2': {
                    'slowStart': {
                    },
                    'maxStreams': {
                    },
                    'payload': {
                        'dataWidth': {
                        },
                        'data': {
                        },
                        'type': {
                        }
                    },
                    'bidirectional': {
                    },
                    'sizeDist': {
                        'type': {
                        },
                        'mixlen9': {
                        },
                        'mixlen10': {
                        },
                        'rate': {
                        },
                        'mixweight1': {
                        },
                        'mixweight3': {
                        },
                        'mixweight2': {
                        },
                        'min': {
                        },
                        'increment': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'max': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixlen2': {
                        },
                        'mixlen1': {
                        },
                        'mixlen4': {
                        },
                        'mixlen3': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixlen7': {
                        },
                        'unit': {
                        },
                        'mixweight10': {
                        }
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationFrames': {
                        },
                        'durationTime': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        },
                        'udfMode': {
                        },
                        'udfLength': {
                        }
                    },
                    'advanced': {
                        'ethTypeField': {
                        },
                        'ethTypeVal': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'increment': {
                        },
                        'unit': {
                        },
                        'rate': {
                        },
                        'max': {
                        },
                        'ramptype': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:stackscrambler': {
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
                        }
                    },
                    'payload': {
                        'transport': {
                        },
                        'data': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'prng': {
                        'seed': {
                        },
                        'offset': {
                        }
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
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
                    'scrambleOptions': {
                        'badL4HeaderLength': {
                        },
                        'badSCTPFlags': {
                        },
                        'badICMPType': {
                        },
                        'badIPProtocol': {
                        },
                        'badGTPSeqno': {
                        },
                        'badICMPCode': {
                        },
                        'badGTPNext': {
                        },
                        'badIPVersion': {
                        },
                        'badGTPLen': {
                        },
                        'badTCPOptions': {
                        },
                        'badIPFlowLabel': {
                        },
                        'badIPFlags': {
                        },
                        'badGTPFlags': {
                        },
                        'badIPChecksum': {
                        },
                        'badEthType': {
                        },
                        'badIPTotalLength': {
                        },
                        'badSCTPLength': {
                        },
                        'badIPOptions': {
                        },
                        'badIPFragOffset': {
                        },
                        'badIPLength': {
                        },
                        'badGTPType': {
                        },
                        'badIPTTL': {
                        },
                        'maxCorruptions': {
                        },
                        'badL4Checksum': {
                        },
                        'badGTPNpdu': {
                        },
                        'badSCTPType': {
                        },
                        'badTCPFlags': {
                        },
                        'badUrgentPointer': {
                        },
                        'badSCTPChecksum': {
                        },
                        'handshakeTCP': {
                        },
                        'badIPTOS': {
                        },
                        'badSCTPVerificationTag': {
                        }
                    }
                },
                '@type:layer4': {
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
                        }
                    },
                    'payload': {
                        'add_timestamp': {
                        },
                        'transport': {
                        },
                        'data': {
                        },
                        'http_type': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'packetsPerSession': {
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    },
                    'payloadSizeDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:layer3advanced': {
                    'advancedIPv6': {
                        'extensionHeaderField': {
                        },
                        'lengthVal': {
                        },
                        'nextHeader': {
                        },
                        'hopLimit': {
                        },
                        'extensionHeaderData': {
                        },
                        'flowLabel': {
                        },
                        'trafficClass': {
                        },
                        'lengthField': {
                        }
                    },
                    'payload': {
                        'dataWidth': {
                        },
                        'data': {
                        },
                        'type': {
                        }
                    },
                    'advancedIPv4': {
                        'tos': {
                        },
                        'lengthVal': {
                        },
                        'optionHeaderData': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        },
                        'lengthField': {
                        },
                        'ttl': {
                        },
                        'optionHeaderField': {
                        }
                    },
                    'bidirectional': {
                    },
                    'sizeDist': {
                        'type': {
                        },
                        'mixlen9': {
                        },
                        'mixlen10': {
                        },
                        'rate': {
                        },
                        'mixweight1': {
                        },
                        'mixweight3': {
                        },
                        'mixweight2': {
                        },
                        'min': {
                        },
                        'increment': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'max': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixlen2': {
                        },
                        'mixlen1': {
                        },
                        'mixlen4': {
                        },
                        'mixlen3': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixlen7': {
                        },
                        'unit': {
                        },
                        'mixweight10': {
                        }
                    },
                    'slowStartFps': {
                    },
                    'enableTCP': {
                    },
                    'slowStart': {
                    },
                    'tuple_gen_seed': {
                    },
                    'enablePerStreamStats': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
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
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        },
                        'udfMode': {
                        },
                        'udfLength': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'increment': {
                        },
                        'unit': {
                        },
                        'rate': {
                        },
                        'max': {
                        },
                        'ramptype': {
                        },
                        'type': {
                        }
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        },
                        'lengthField': {
                        }
                    }
                },
                '@type:layer3': {
                    'dstPortMask': {
                    },
                    'srcPort': {
                    },
                    'maxStreams': {
                    },
                    'advancedIPv6': {
                        'extensionHeaderField': {
                        },
                        'lengthVal': {
                        },
                        'nextHeader': {
                        },
                        'hopLimit': {
                        },
                        'extensionHeaderData': {
                        },
                        'flowLabel': {
                        },
                        'trafficClass': {
                        },
                        'lengthField': {
                        }
                    },
                    'syncIP': {
                    },
                    'payload': {
                        'dataWidth': {
                        },
                        'data': {
                        },
                        'type': {
                        }
                    },
                    'advancedIPv4': {
                        'tos': {
                        },
                        'lengthVal': {
                        },
                        'optionHeaderData': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        },
                        'lengthField': {
                        },
                        'ttl': {
                        },
                        'optionHeaderField': {
                        }
                    },
                    'bidirectional': {
                    },
                    'sizeDist': {
                        'type': {
                        },
                        'mixlen9': {
                        },
                        'mixlen10': {
                        },
                        'rate': {
                        },
                        'mixweight1': {
                        },
                        'mixweight3': {
                        },
                        'mixweight2': {
                        },
                        'min': {
                        },
                        'increment': {
                        },
                        'mixweight8': {
                        },
                        'mixweight9': {
                        },
                        'max': {
                        },
                        'mixweight6': {
                        },
                        'mixweight7': {
                        },
                        'mixweight4': {
                        },
                        'mixweight5': {
                        },
                        'mixlen2': {
                        },
                        'mixlen1': {
                        },
                        'mixlen4': {
                        },
                        'mixlen3': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixlen7': {
                        },
                        'unit': {
                        },
                        'mixweight10': {
                        }
                    },
                    'udpDstPortMode': {
                    },
                    'addrGenMode': {
                    },
                    'slowStartFps': {
                    },
                    'enableTCP': {
                    },
                    'dstPort': {
                    },
                    'slowStart': {
                    },
                    'udpSrcPortMode': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'randomizeIP': {
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
                    'srcPortMask': {
                    },
                    'payloadAdvanced': {
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        },
                        'udfMode': {
                        },
                        'udfLength': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'increment': {
                        },
                        'unit': {
                        },
                        'rate': {
                        },
                        'max': {
                        },
                        'ramptype': {
                        },
                        'type': {
                        }
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        },
                        'lengthField': {
                        }
                    }
                },
                '@type:playback': {
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
                        }
                    },
                    'behavior': {
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'modification': {
                        'originalport': {
                        },
                        'replay': {
                        },
                        'single': {
                        },
                        'startpacket': {
                        },
                        'loopcount': {
                        },
                        'endpacket': {
                        },
                        'newport': {
                        },
                        'independentflows': {
                        },
                        'serveripinjection': {
                        },
                        'bpfstring': {
                        }
                    },
                    'file': {
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:security_np': {
                    'sessions': {
                        'max': {
                        },
                        'maxPerSecond': {
                        }
                    },
                    'randomSeed': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'attackPlan': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'delayStart': {
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    },
                    'attackRetries': {
                    }
                },
                '@type:appsim': {
                    'app': {
                        'removedns': {
                        },
                        'fidelity': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'replace_streams': {
                        }
                    },
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
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
                        'server_record_len': {
                        },
                        'client_record_len': {
                        },
                        'ssl_keylog_max_entries': {
                        },
                        'sslReuseType': {
                        }
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    },
                    'profile': {
                    }
                },
                '@type:security_all': {
                    'maxPacketsPerSecond': {
                    },
                    'randomSeed': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'maxConcurrAttacks': {
                    },
                    'attackPlan': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'delayStart': {
                    },
                    'maxAttacksPerSecond': {
                    },
                    'attackRetries': {
                    }
                },
                '@type:clientsim': {
                    'app': {
                        'removedns': {
                        },
                        'fidelity': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'replace_streams': {
                        }
                    },
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
                        }
                    },
                    'ssl': {
                        'ssl_client_keylog': {
                        },
                        'server_record_len': {
                        },
                        'client_record_len': {
                        },
                        'ssl_keylog_max_entries': {
                        },
                        'sslReuseType': {
                        }
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'superflow': {
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:liveappsim': {
                    'tputscalefactor': {
                    },
                    'app': {
                        'removeUnknownTcpUdp': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'replace_streams': {
                        },
                        'removeUnknownSSL': {
                        }
                    },
                    'sessions': {
                        'max': {
                        },
                        'closeFast': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'targetPerSecond': {
                        },
                        'openFast': {
                        },
                        'targetMatches': {
                        },
                        'maxActive': {
                        },
                        'allocationOverride': {
                        },
                        'maxPerSecond': {
                        },
                        'target': {
                        },
                        'emphasis': {
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
                    'concurrencyscalefactor': {
                    },
                    'ip6': {
                        'hop_limit': {
                        },
                        'flowlabel': {
                        },
                        'traffic_class': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'increment': {
                        },
                        'max': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'liveProfile': {
                    },
                    'sfratescalefactor': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'rampDist': {
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'upBehavior': {
                        },
                        'synRetryMode': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'steady': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'delayStart': {
                    },
                    'tcp': {
                        'delay_acks': {
                        },
                        'retry_quantum_ms': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'reset_at_end': {
                        },
                        'disable_ack_piggyback': {
                        },
                        'tcp_icw': {
                        },
                        'aging_time_data_type': {
                        },
                        'delay_acks_ms': {
                        },
                        'aging_time': {
                        },
                        'tcp_window_scale': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'add_timestamps': {
                        },
                        'ack_every_n': {
                        },
                        'mss': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_4_way_close': {
                        },
                        'handshake_data': {
                        },
                        'raw_flags': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'initial_receive_window': {
                        },
                        'retries': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        }
                    },
                    'inflateDeflate': {
                    },
                    'rateDist': {
                        'min': {
                        },
                        'unit': {
                        },
                        'max': {
                        },
                        'scope': {
                        },
                        'unlimited': {
                        },
                        'type': {
                        }
                    }
                },
                'type': {
                },
                'createdOn': {
                },
                'id': {
                },
                'author': {
                },
                'revision': {
                },
                'createdBy': {
                },
                'description': {
                },
                'active': {
                },
                'contentType': {
                },
                'originalPresetLabel': {
                },
                'operations': {
                    'getComponentPresetNames': [{
                    }]
                }
            }],
            'description': {
            },
            'name': {
            },
            'contentType': {
            },
            'operations': {
                'search': [{
                }],
                'run': [{
                }],
                'clone': [{
                }],
                'importModel': [{
                }],
                'stopRun': [{
                }],
                'realTimeStats': [{
                }],
                'add': [{
                }],
                'delete': [{
                }],
                'exportModel': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'remove': [{
                }],
                'load': [{
                }],
                'new': [{
                }]
            }
        },
        'evasionProfile': {
            'createdOn': {
            },
            'author': {
            },
            'revision': {
            },
            'createdBy': {
            },
            'lockedBy': {
            },
            'description': {
            },
            'name': {
            },
            'label': {
            },
            'StrikeOptions': {
                'UDP': {
                    'SourcePort': {
                    },
                    'DestinationPort': {
                    },
                    'DestinationPortType': {
                    },
                    'SourcePortType': {
                    }
                },
                'Ethernet': {
                    'MTU': {
                    }
                },
                'DCERPC': {
                    'MultiContextBind': {
                    },
                    'MultiContextBindTail': {
                    },
                    'MultiContextBindHead': {
                    },
                    'MaxFragmentSize': {
                    },
                    'UseObjectID': {
                    }
                },
                'HTTP': {
                    'DirectoryFakeRelative': {
                    },
                    'EncodeUnicodeRandom': {
                    },
                    'EncodeUnicodePercentU': {
                    },
                    'AuthenticationType': {
                    },
                    'VersionUse0_9': {
                    },
                    'EncodeUnicodeAll': {
                    },
                    'EndRequestFakeHTTPHeader': {
                    },
                    'Password': {
                    },
                    'RequireLeadingSlash': {
                    },
                    'ServerChunkedTransferSize': {
                    },
                    'ClientChunkedTransfer': {
                    },
                    'MethodRandomInvalid': {
                    },
                    'DirectorySelfReference': {
                    },
                    'EncodeHexAll': {
                    },
                    'ServerChunkedTransfer': {
                    },
                    'EncodeSecondNibbleHex': {
                    },
                    'EncodeFirstNibbleHex': {
                    },
                    'MethodURITabs': {
                    },
                    'HTTPServerProfile': {
                    },
                    'IgnoreHeaders': {
                    },
                    'Base64EncodePOSTData': {
                    },
                    'MethodURISpaces': {
                    },
                    'ServerCompression': {
                    },
                    'EncodeUnicodeBareByte': {
                    },
                    'VersionRandomizeCase': {
                    },
                    'VirtualHostnameType': {
                    },
                    'EncodeUnicodeInvalid': {
                    },
                    'EncodeDoublePercentHex': {
                    },
                    'EncodeDoubleNibbleHex': {
                    },
                    'PadHTTPPost': {
                    },
                    'EncodeHexRandom': {
                    },
                    'MethodRandomizeCase': {
                    },
                    'URIAppendAltSpacesSize': {
                    },
                    'URIRandomizeCase': {
                    },
                    'VersionRandomInvalid': {
                    },
                    'ForwardToBackSlashes': {
                    },
                    'URIPrependAltSpacesSize': {
                    },
                    'VirtualHostname': {
                    },
                    'HTTPTransportMethods': {
                    },
                    'ClientChunkedTransferSize': {
                    },
                    'RequestFullURL': {
                    },
                    'ShuffleHeaders': {
                    },
                    'Username': {
                    },
                    'PostParameterRandomPrepend': {
                    },
                    'MethodURINull': {
                    },
                    'URIAppendAltSpaces': {
                    },
                    'GetParameterRandomPrepend': {
                    },
                    'URIPrependAltSpaces': {
                    }
                },
                'FILETRANSFER': {
                    'SmtpEncoding': {
                    },
                    'CompressionMethod': {
                    },
                    'Pop3Encoding': {
                    },
                    'FtpTransferMethod': {
                    },
                    'TransportProtocol': {
                    },
                    'Imap4Encoding': {
                    }
                },
                'MALWARE': {
                    'FilenameInsertEnvVar': {
                    },
                    'SmtpEncoding': {
                    },
                    'CompressionMethod': {
                    },
                    'Pop3Encoding': {
                    },
                    'FtpTransferMethod': {
                    },
                    'TransportProtocol': {
                    },
                    'Imap4Encoding': {
                    }
                },
                'RTF': {
                    'ASCII_Escaping': {
                    },
                    'FictitiousCW': {
                    },
                    'WhiteSpace': {
                    },
                    'MixedCase': {
                    }
                },
                'ICMP': {
                    'DoEcho': {
                    }
                },
                'HTML': {
                    'HTMLUnicodeUTF8EncodingMode': {
                    },
                    'HTMLUnicodeEncoding': {
                    },
                    'HTMLUnicodeUTF8EncodingSize': {
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
                'OLE': {
                    'RefragmentData': {
                    }
                },
                'Global': {
                    'AllowDeprecated': {
                    },
                    'BehaviorOnTimeout': {
                    },
                    'FalsePositives': {
                    },
                    'CachePoisoning': {
                    },
                    'MaxTimeoutPerStrike': {
                    },
                    'IOTimeout': {
                    }
                },
                'COMMAND': {
                    'Malicious': {
                    },
                    'PadPathSlashes': {
                    },
                    'PadCommandWhitespace': {
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
                'PDF': {
                    'RandomizeDictKeyOrder': {
                    },
                    'HexEncodeNames': {
                    },
                    'ShortFilterNames': {
                    },
                    'Version': {
                    },
                    'PreHeaderData': {
                    }
                },
                'SSL': {
                    'DestPortOverride': {
                    },
                    'SecurityProtocol': {
                    },
                    'EnableOnAllTCP': {
                    },
                    'ServerCertificateFile': {
                    },
                    'ServerKeyFile': {
                    },
                    'DisableDefaultStrikeSSL': {
                    },
                    'EnableOnAllHTTP': {
                    },
                    'Cipher': {
                    },
                    'ClientKeyFile': {
                    },
                    'ClientCertificateFile': {
                    }
                },
                'FTP': {
                    'AuthenticationType': {
                    },
                    'FTPEvasionLevel': {
                    },
                    'Password': {
                    },
                    'Username': {
                    },
                    'PadCommandWhitespace': {
                    }
                },
                'SIP': {
                    'EnvelopeType': {
                    },
                    'RandomizeCase': {
                    },
                    'PadHeadersLineBreak': {
                    },
                    'ShuffleHeaders': {
                    },
                    'To': {
                    },
                    'CompactHeaders': {
                    },
                    'PadHeadersWhitespace': {
                    },
                    'From': {
                    }
                },
                'Variations': {
                    'Shuffle': {
                    },
                    'VariantTesting': {
                    },
                    'TestType': {
                    },
                    'Subset': {
                    },
                    'Limit': {
                    }
                },
                'IP': {
                    'FragPolicy': {
                    },
                    'RFC3128FakePort': {
                    },
                    'MaxReadSize': {
                    },
                    'RFC3128': {
                    },
                    'TTL': {
                    },
                    'MaxFragSize': {
                    },
                    'FragOrder': {
                    },
                    'TOS': {
                    },
                    'IPEvasionsOnBothSides': {
                    },
                    'RFC3514': {
                    },
                    'ReadWriteWindowSize': {
                    },
                    'MaxWriteSize': {
                    },
                    'FragEvasion': {
                    }
                },
                'MS_Exchange_Ports': {
                    'SystemAttendant': {
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
                'SMB': {
                    'AuthenticationType': {
                    },
                    'MaxReadSize': {
                    },
                    'Password': {
                    },
                    'Username': {
                    },
                    'RandomPipeOffset': {
                    },
                    'MaxWriteSize': {
                    }
                },
                'UNIX': {
                    'PadPathSlashes': {
                    },
                    'PadCommandWhitespace': {
                    }
                },
                'TCP': {
                    'SegmentOrder': {
                    },
                    'SkipHandshake': {
                    },
                    'DuplicateNullFlags': {
                    },
                    'DuplicateLastSegment': {
                    },
                    'AcknowledgeAllSegments': {
                    },
                    'SourcePort': {
                    },
                    'DestinationPort': {
                    },
                    'SourcePortType': {
                    },
                    'DestinationPortType': {
                    },
                    'DuplicateBadSeq': {
                    },
                    'DuplicateBadSyn': {
                    },
                    'MaxSegmentSize': {
                    },
                    'DuplicateBadChecksum': {
                    },
                    'DuplicateBadReset': {
                    },
                    'SneakAckHandshake': {
                    }
                },
                'SNMP': {
                    'CommunityString': {
                    }
                },
                'SMTP': {
                    'ShuffleHeaders': {
                    },
                    'SMTPUseProxyMode': {
                    },
                    'PadCommandWhitespace': {
                    }
                },
                'SHELLCODE': {
                    'RandomNops': {
                    }
                },
                'SUNRPC': {
                    'TCPFragmentSize': {
                    },
                    'OneFragmentMultipleTCPSegmentsCount': {
                    },
                    'RPCFragmentTCPSegmentDistribution': {
                    },
                    'NullCredentialPadding': {
                    }
                },
                'SELF': {
                    'TraversalRequestFilename': {
                    },
                    'DelaySeconds': {
                    },
                    'AS-ID': {
                    },
                    'MaximumIterations': {
                    },
                    'Password': {
                    },
                    'StartingFuzzerOffset': {
                    },
                    'EndingFuzzerOffset': {
                    },
                    'MaximumRuntime': {
                    },
                    'Repetitions': {
                    },
                    'FileTransferRandCase': {
                    },
                    'TraversalVirtualDirectory': {
                    },
                    'ReportCLSIDs': {
                    },
                    'FileTransferFile': {
                    },
                    'URI': {
                    },
                    'HTMLPadding': {
                    },
                    'AppSimUseNewTuple': {
                    },
                    'ROUTER-ID': {
                    },
                    'AppSimSmartflow': {
                    },
                    'FileTransferExtension': {
                    },
                    'AppSimSuperflow': {
                    },
                    'AREA-ID': {
                    },
                    'TraversalWindowsDirectory': {
                    },
                    'UnicodeTraversalWindowsDirectory': {
                    },
                    'UnicodeTraversalVirtualDirectory': {
                    },
                    'Username': {
                    },
                    'AppSimAppProfile': {
                    },
                    'ApplicationPings': {
                    },
                    'FileTransferName': {
                    }
                },
                'POP3': {
                    'AuthenticationType': {
                    },
                    'Password': {
                    },
                    'Username': {
                    },
                    'POP3UseProxyMode': {
                    },
                    'PadCommandWhitespace': {
                    }
                },
                'operations': {
                    'getStrikeOptions': [{
                        'choice': [{
                            'description': {
                            },
                            'name': {
                            },
                            'label': {
                            }
                        }],
                        'description': {
                        },
                        'name': {
                        },
                        'label': {
                        },
                        'realtimeGroup': {
                        },
                        'units': {
                        }
                    }]
                }
            },
            'contentType': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'delete': [{
                }]
            }
        },
        'topology': {
            'model': {
            },
            'ixoslicensed': {
            },
            'runningTest': [{
                'port': [{
                }],
                'progress': {
                },
                'result': {
                },
                'currentTest': {
                },
                'capturing': {
                },
                'state': {
                },
                'runtime': {
                },
                'label': {
                },
                'testid': {
                },
                'initProgress': {
                },
                'user': {
                },
                'phase': {
                },
                'timeRemaining': {
                },
                'completed': {
                }
            }],
            'ixos': {
            },
            'slot': [{
                'id': {
                },
                'port': [{
                    'id': {
                    },
                    'model': {
                    },
                    'exportProgress': {
                    },
                    'capturing': {
                    },
                    'owner': {
                    },
                    'number': {
                    },
                    'reservedBy': {
                    },
                    'group': {
                    },
                    'note': {
                    },
                    'speed': {
                    },
                    'link': {
                    },
                    'state': {
                    }
                }],
                'model': {
                },
                'mode': {
                },
                'state': {
                }
            }],
            'serialNumber': {
            },
            'operations': {
                'run': [{
                }],
                'exportCapture': [{
                }],
                'stopRun': [{
                }],
                'reserve': [{
                }],
                'addPortNote': [{
                }],
                'setCardMode': [{
                }],
                'setCardSpeed': [{
                }],
                'setCardFanout': [{
                }],
                'setPerfAcc': [{
                }],
                'reboot': [{
                }],
                'unreserve': [{
                }]
            }
        },
        'superflow': {
            'estimate_flows': {
            },
            'weight': {
            },
            'lockedBy': {
            },
            'seed': {
            },
            'label': {
            },
            'percentBandwidth': {
            },
            'percentFlows': {
            },
            'flows': [{
                'id': {
                },
                'to': {
                },
                'flowcount': {
                },
                'name': {
                },
                'singleNP': {
                },
                'label': {
                },
                'from': {
                },
                'params': {
                },
                'operations': {
                    'getCannedFlows': [{
                    }],
                    'getFlowChoices': [{
                        'createdOn': {
                        },
                        'author': {
                        },
                        'revision': {
                        },
                        'createdBy': {
                        },
                        'lockedBy': {
                        },
                        'description': {
                        },
                        'label': {
                        },
                        'contentType': {
                        }
                    }]
                }
            }],
            'createdOn': {
            },
            'author': {
            },
            'revision': {
            },
            'estimate_bytes': {
            },
            'createdBy': {
            },
            'generated': {
            },
            'description': {
            },
            'name': {
            },
            'hosts': [{
                'id': {
                },
                'iface': {
                },
                'hostname': {
                },
                'ip': {
                    'type': {
                    }
                }
            }],
            'contentType': {
            },
            'actions': [{
                'id': {
                },
                'matchBlock': {
                },
                'flowlabel': {
                },
                'flowid': {
                },
                'source': {
                },
                'exflows': {
                },
                'gotoBlock': {
                },
                'label': {
                },
                'params': {
                },
                'type': {
                },
                'actionInfo': [{
                    'choice': [{
                        'description': {
                        },
                        'name': {
                        },
                        'label': {
                        }
                    }],
                    'description': {
                    },
                    'name': {
                    },
                    'label': {
                    },
                    'realtimeGroup': {
                    },
                    'units': {
                    }
                }],
                'operations': {
                    'getActionInfo': [{
                        'choice': [{
                            'description': {
                            },
                            'name': {
                            },
                            'label': {
                            }
                        }],
                        'description': {
                        },
                        'name': {
                        },
                        'label': {
                        },
                        'realtimeGroup': {
                        },
                        'units': {
                        }
                    }],
                    'getActionChoices': [{
                    }]
                }
            }],
            'operations': {
                'saveAs': [{
                }],
                'save': [{
                }],
                'removeAction': [{
                }],
                'addFlow': [{
                }],
                'delete': [{
                }],
                'removeFlow': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }],
                'addHost': [{
                }],
                'addAction': [{
                }]
            }
        },
        'network': {
            'interfaceCount': {
            },
            'createdOn': {
            },
            'author': {
            },
            'revision': {
            },
            'createdBy': {
            },
            'lockedBy': {
            },
            'description': {
            },
            'name': {
            },
            'networkModel': {
                'ip6_router': [{
                    'prefix_length': {
                    },
                    'ip_address': {
                    },
                    'hosts_ip_alloc_container': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'enodeb_mme6': [{
                    'prefix_length': {
                    },
                    'mme_ip_address': {
                    },
                    'default_container': {
                    },
                    'ue_address': {
                    },
                    'ip_allocation_mode': {
                    },
                    'dns': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'enodebs': [{
                        'prefix_length': {
                        },
                        'ip_address': {
                        },
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'gateway_ip_address': {
                        }
                    }],
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'sgw_ip_address': {
                    }
                }],
                'ue_info': [{
                    'count': {
                    },
                    'msisdn_base': {
                    },
                    'secret_key_step': {
                    },
                    'imei_base': {
                    },
                    'operator_variant': {
                    },
                    'maxmbps_per_ue': {
                    },
                    'imsi_base': {
                    },
                    'id': {
                    },
                    'secret_key': {
                    },
                    'mobility_session_infos': [{
                        'id': {
                        },
                        'value': {
                        }
                    }]
                }],
                'ip_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'ip_router': [{
                    'ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'slaac_cfg': [{
                    'use_rand_addr': {
                    },
                    'stateless_dhcpv6c_cfg': {
                    },
                    'enable_dad': {
                    },
                    'id': {
                    },
                    'fallback_ip_address': {
                    }
                }],
                'pgw': [{
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'default_container': {
                    },
                    'plmn': {
                    },
                    'max_sessions': {
                    },
                    'dns': {
                    },
                    'lease_address_v6': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'path_advanced': [{
                    'tags': {
                    },
                    'source_port_algorithm': {
                    },
                    'destination_port_base': {
                    },
                    'enable_external_file': {
                    },
                    'stream_group': {
                    },
                    'destination_port_algorithm': {
                    },
                    'source_container': {
                    },
                    'source_port_base': {
                    },
                    'source_port_count': {
                    },
                    'tuple_limit': {
                    },
                    'file': {
                    },
                    'destination_port_count': {
                    },
                    'xor_bits': {
                    },
                    'id': {
                    },
                    'destination_container': {
                    }
                }],
                'enodeb_mme': [{
                    'mme_ip_address': {
                    },
                    'default_container': {
                    },
                    'ue_address': {
                    },
                    'ip_allocation_mode': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'enodebs': [{
                        'ip_address': {
                        },
                        'default_container': {
                        },
                        'enodebCount': {
                        },
                        'gateway_ip_address': {
                        },
                        'netmask': {
                        }
                    }],
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'sgw_ip_address': {
                    }
                }],
                'enodeb_mme_sgw': [{
                    'mme_ip_address': {
                    },
                    'default_container': {
                    },
                    'ue_address': {
                    },
                    'ip_allocation_mode': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'sgsn6': [{
                    'prefix_length': {
                    },
                    'ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_ip_address': {
                    }
                }],
                'sgsn': [{
                    'ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'ggsn_ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'ip_dhcp_hosts': [{
                    'tags': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'accept_local_offers_only': {
                    },
                    'ldap': {
                    },
                    'dns_proxy': {
                    },
                    'proxy': {
                    },
                    'allocation_rate': {
                    },
                    'id': {
                    },
                    'enable_stats': {
                    },
                    'behind_snapt': {
                    }
                }],
                'ds_lite_aftr': [{
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'ip_address': {
                    },
                    'b4_ip_address': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'b4_count': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ip6_dns_proxy': [{
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'dns_proxy_ip_count': {
                    },
                    'id': {
                    }
                }],
                'ip6_static_hosts': [{
                    'tags': {
                    },
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'host_ipv6_addr_alloc_mode': {
                    },
                    'dns': {
                    },
                    'maxmbps_per_host': {
                    },
                    'ip_alloc_container': {
                    },
                    'ip_address': {
                    },
                    'ip_selection_type': {
                    },
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'dns_proxy': {
                    },
                    'proxy': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
                    }
                }],
                'enodeb': [{
                    'default_container': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'sctp_over_udp': {
                    },
                    'plmn': {
                    },
                    'enodebs': [{
                        'mme_ip_address': {
                        },
                        'ip_address': {
                        },
                        'enodebCount': {
                        }
                    }],
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'sctp_sport': {
                    }
                }],
                'enodeb_mme_sgw6': [{
                    'mme_ip_address': {
                    },
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'ue_address': {
                    },
                    'ip_allocation_mode': {
                    },
                    'dns': {
                    },
                    'pgw_ip_address': {
                    },
                    'plmn': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ip_external_hosts': [{
                    'tags': {
                    },
                    'ip_address': {
                    },
                    'count': {
                    },
                    'proxy': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    }
                }],
                'mobility_session_info': [{
                    'bearers': [{
                        'qci_label': {
                        }
                    }],
                    'username': {
                    },
                    'initiated_dedicated_bearers': {
                    },
                    'access_point_name': {
                    },
                    'id': {
                    },
                    'password': {
                    }
                }],
                'ip6_dhcp_server': [{
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'ia_type': {
                    },
                    'offer_lifetime': {
                    },
                    'pool_size': {
                    },
                    'pool_dns_address1': {
                    },
                    'pool_prefix_length': {
                    },
                    'ip_address': {
                    },
                    'pool_dns_address2': {
                    },
                    'max_lease_time': {
                    },
                    'pool_base_address': {
                    },
                    'default_lease_time': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ip_dhcp_server': [{
                    'default_container': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'accept_local_requests_only': {
                    },
                    'netmask': {
                    },
                    'ip_address': {
                    },
                    'lease_time': {
                    },
                    'lease_address': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ue': [{
                    'tags': {
                    },
                    'ue_info': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'request_ipv6': {
                    },
                    'mobility_with_traffic': {
                    },
                    'allocation_rate': {
                    },
                    'proxy': {
                    },
                    'mobility_interval_ms': {
                    },
                    'id': {
                    },
                    'enable_stats': {
                    },
                    'behind_snapt': {
                    },
                    'mobility_action': {
                    }
                }],
                'ip_dns_proxy': [{
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'dns_proxy_ip_count': {
                    },
                    'id': {
                    }
                }],
                'dhcpv6c_tout_and_retr_cfg': [{
                    'dhcp6c_initial_sol_tout': {
                    },
                    'dhcp6c_inforeq_attempts': {
                    },
                    'dhcp6c_sol_attempts': {
                    },
                    'dhcp6c_max_rebind_tout': {
                    },
                    'dhcp6c_max_renew_tout': {
                    },
                    'dhcp6c_req_attempts': {
                    },
                    'dhcp6c_max_inforeq_tout': {
                    },
                    'dhcp6c_initial_inforeq_tout': {
                    },
                    'dhcp6c_release_attempts': {
                    },
                    'dhcp6c_initial_release_tout': {
                    },
                    'dhcp6c_initial_renew_tout': {
                    },
                    'dhcp6c_max_sol_tout': {
                    },
                    'dhcp6c_initial_req_tout': {
                    },
                    'dhcp6c_initial_rebind_tout': {
                    },
                    'dhcp6c_max_req_tout': {
                    },
                    'id': {
                    }
                }],
                'ggsn6': [{
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'dhcpv6c_req_opts_cfg': [{
                    'dhcpv6v_req_preference': {
                    },
                    'dhcpv6v_req_dns_resolvers': {
                    },
                    'dhcpv6v_req_dns_list': {
                    },
                    'id': {
                    },
                    'dhcpv6v_req_server_id': {
                    }
                }],
                'interface': [{
                    'mtu': {
                    },
                    'duplicate_mac_address': {
                    },
                    'number': {
                    },
                    'packet_filter': {
                        'not_dest_ip': {
                        },
                        'src_port': {
                        },
                        'dest_port': {
                        },
                        'not_src_port': {
                        },
                        'dest_ip': {
                        },
                        'not_dest_port': {
                        },
                        'vlan': {
                        },
                        'not_src_ip': {
                        },
                        'src_ip': {
                        },
                        'not_vlan': {
                        },
                        'filter': {
                        }
                    },
                    'mac_address': {
                    },
                    'use_vnic_mac_address': {
                    },
                    'vlan_key': {
                    },
                    'description': {
                    },
                    'impairments': {
                        'corrupt_rand': {
                        },
                        'corrupt_lt64': {
                        },
                        'rate': {
                        },
                        'frack': {
                        },
                        'drop': {
                        },
                        'corrupt_chksum': {
                        },
                        'corrupt_lt256': {
                        },
                        'corrupt_gt256': {
                        }
                    },
                    'ignore_pause_frames': {
                    },
                    'id': {
                    }
                }],
                'ipsec_config': [{
                    'xauth_password': {
                    },
                    'ike_auth_alg': {
                    },
                    'xauth_username': {
                    },
                    'enable_xauth': {
                    },
                    'ike_pfs': {
                    },
                    'ike_1to1': {
                    },
                    'setup_timeout': {
                    },
                    'dpd_timeout': {
                    },
                    'esp_auth_alg': {
                    },
                    'psk': {
                    },
                    'dpd_delay': {
                    },
                    'retrans_interval': {
                    },
                    'ike_prf_alg': {
                    },
                    'nat_traversal': {
                    },
                    'esp_encr_alg': {
                    },
                    'ike_encr_alg': {
                    },
                    'max_outstanding': {
                    },
                    'ike_mode': {
                    },
                    'left_id': {
                    },
                    'ipsec_lifetime': {
                    },
                    'right_id': {
                    },
                    'ike_lifetime': {
                    },
                    'dpd_enabled': {
                    },
                    'wildcard_tsr': {
                    },
                    'rekey_margin': {
                    },
                    'ike_dh': {
                    },
                    'init_rate': {
                    },
                    'initial_contact': {
                    },
                    'debug_log': {
                    },
                    'id': {
                    },
                    'ike_version': {
                    }
                }],
                'ip_static_hosts': [{
                    'tags': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'maxmbps_per_host': {
                    },
                    'netmask': {
                    },
                    'ip_address': {
                    },
                    'ldap': {
                    },
                    'ip_selection_type': {
                    },
                    'mpls_list': [{
                        'id': {
                        },
                        'value': {
                        }
                    }],
                    'dns_proxy': {
                    },
                    'proxy': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
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
                'ip6_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'ds_lite_b4': [{
                    'prefix_length': {
                    },
                    'host_ip_addr_alloc_mode': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'aftr_count': {
                    },
                    'host_ip_base_addr': {
                    },
                    'ip_address': {
                    },
                    'hosts_ip_increment': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'aftr_addr': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'enodeb6': [{
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'sctp_over_udp': {
                    },
                    'plmn': {
                    },
                    'enodebs': [{
                        'mme_ip_address': {
                        },
                        'ip_address': {
                        },
                        'enodebCount': {
                        }
                    }],
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'sctp_sport': {
                    }
                }],
                'sixrd_ce': [{
                    'hosts_per_ce': {
                    },
                    'tags': {
                    },
                    'default_container': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'ip4_mask_length': {
                    },
                    'ip_address': {
                    },
                    'sixrd_prefix_length': {
                    },
                    'sixrd_prefix': {
                    },
                    'br_ip_address': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'enable_stats': {
                    }
                }],
                'dhcpv6c_cfg': [{
                    'dhcp6c_tout_and_retr_config': {
                    },
                    'dhcp6c_ia_t1': {
                    },
                    'dhcp6c_ia_t2': {
                    },
                    'dhcp6c_renew_timer': {
                    },
                    'dhcp6c_max_outstanding': {
                    },
                    'dhcp6c_ia_type': {
                    },
                    'dhcp6c_req_opts_config': {
                    },
                    'id': {
                    },
                    'dhcp6c_duid_type': {
                    },
                    'dhcp6c_initial_srate': {
                    }
                }],
                'plmn': [{
                    'mcc': {
                    },
                    'description': {
                    },
                    'mnc': {
                    },
                    'id': {
                    }
                }],
                'sgw_pgw6': [{
                    'sgw_advertised_sgw': {
                    },
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'max_sessions': {
                    },
                    'id': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'path_basic': [{
                    'id': {
                    },
                    'source_container': {
                    },
                    'destination_container': {
                    }
                }],
                'pgw6': [{
                    'prefix_length': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'default_container': {
                    },
                    'plmn': {
                    },
                    'max_sessions': {
                    },
                    'dns': {
                    },
                    'lease_address_v6': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'vlan': [{
                    'mtu': {
                    },
                    'default_container': {
                    },
                    'inner_vlan': {
                    },
                    'duplicate_mac_address': {
                    },
                    'mac_address': {
                    },
                    'tpid': {
                    },
                    'description': {
                    },
                    'id': {
                    },
                    'outer_vlan': {
                    }
                }],
                'sgw_pgw': [{
                    'sgw_advertised_sgw': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'max_sessions': {
                    },
                    'id': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ip_ldap_server': [{
                    'auth_timeout': {
                    },
                    'authentication_rate': {
                    },
                    'ldap_username_start_tag': {
                    },
                    'ldap_user_count': {
                    },
                    'ldap_server_address': {
                    },
                    'dn_fixed_val': {
                    },
                    'ldap_user_min': {
                    },
                    'ldap_user_max': {
                    },
                    'ldap_password_start_tag': {
                    },
                    'id': {
                    }
                }],
                'ip6_external_hosts': [{
                    'tags': {
                    },
                    'ip_address': {
                    },
                    'count': {
                    },
                    'proxy': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    }
                }],
                'mme_sgw_pgw6': [{
                    'sgw_advertised_sgw': {
                    },
                    'ue_info': {
                    },
                    'prefix_length': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'max_sessions': {
                    },
                    'id': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'ipsec_router': [{
                    'ip_address': {
                    },
                    'default_container': {
                    },
                    'ipsec': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    },
                    'ike_peer_ip_address': {
                    },
                    'netmask': {
                    }
                }],
                'ggsn': [{
                    'default_container': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'netmask': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'id': {
                    },
                    'gateway_ip_address': {
                    }
                }],
                'mme_sgw_pgw': [{
                    'sgw_advertised_sgw': {
                    },
                    'ue_info': {
                    },
                    'default_container': {
                    },
                    'dns': {
                    },
                    'netmask': {
                    },
                    'ip_address': {
                    },
                    'lease_address': {
                    },
                    'plmn': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'max_sessions': {
                    },
                    'id': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    }
                }]
            },
            'label': {
            },
            'contentType': {
            },
            'operations': {
                'search': [{
                }],
                'importNetwork': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'delete': [{
                }],
                'list': [{
                }],
                'load': [{
                }],
                'new': [{
                }]
            }
        },
        'appProfile': {
            'createdOn': {
            },
            'weightType': {
            },
            'author': {
            },
            'revision': {
            },
            'createdBy': {
            },
            'lockedBy': {
            },
            'description': {
            },
            'name': {
            },
            'label': {
            },
            'superflow': [{
                'estimate_flows': {
                },
                'weight': {
                },
                'lockedBy': {
                },
                'seed': {
                },
                'label': {
                },
                'percentBandwidth': {
                },
                'percentFlows': {
                },
                'flows': [{
                    'id': {
                    },
                    'to': {
                    },
                    'flowcount': {
                    },
                    'name': {
                    },
                    'singleNP': {
                    },
                    'label': {
                    },
                    'from': {
                    },
                    'params': {
                    }
                }],
                'createdOn': {
                },
                'author': {
                },
                'revision': {
                },
                'estimate_bytes': {
                },
                'createdBy': {
                },
                'generated': {
                },
                'description': {
                },
                'name': {
                },
                'hosts': [{
                    'id': {
                    },
                    'iface': {
                    },
                    'hostname': {
                    },
                    'ip': {
                        'type': {
                        }
                    }
                }],
                'contentType': {
                },
                'actions': [{
                    'id': {
                    },
                    'matchBlock': {
                    },
                    'flowlabel': {
                    },
                    'flowid': {
                    },
                    'source': {
                    },
                    'exflows': {
                    },
                    'gotoBlock': {
                    },
                    'label': {
                    },
                    'params': {
                    },
                    'type': {
                    }
                }]
            }],
            'contentType': {
            },
            'operations': {
                'remove': [{
                }],
                'delete': [{
                }],
                'recompute': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'importAppProfile': [{
                }],
                'search': [{
                }],
                'exportAppProfile': [{
                }],
                'add': [{
                }],
                'load': [{
                }],
                'new': [{
                }]
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
                'getHistoricalSeries': [{
                }],
                'getHistoricalResultSize': [{
                }],
                'getGroups': [{
                    'createdOn': {
                    },
                    'author': {
                    },
                    'revision': {
                    },
                    'createdBy': {
                    },
                    'lockedBy': {
                    },
                    'description': {
                    },
                    'label': {
                    },
                    'contentType': {
                    }
                }]
            }
        }],
        'reports': {
            'endtime': {
            },
            'result': {
            },
            'starttime': {
            },
            'isPartOfResiliency': {
            },
            'label': {
            },
            'testid': {
            },
            'network': {
            },
            'iteration': {
            },
            'size': {
            },
            'duration': {
            },
            'testname': {
            },
            'name': {
            },
            'user': {
            },
            'operations': {
                'search': [{
                }],
                'exportReport': [{
                }],
                'delete': [{
                }],
                'getReportContents': [{
                }],
                'getReportTable': [{
                }]
            }
        },
        'capture': {
            'operations': {
                'importCapture': [{
                }]
            }
        }
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
    def _decorate_model_object(obj):
        (data_model_path, data_model) = DataModelMeta._get_from_model(obj.__data_model_path__())
        if data_model is None:
            return obj
        if isinstance(data_model, list):
            setattr(obj, '_getitem_', lambda x: DataModelProxy(wrapper=obj._wrapper, name=str(x), path=obj.__full_path__(), model_path=obj.__data_model_path__()))
            data_model = data_model[0]
        for key in data_model:
            if key.startswith("@"):
                continue
            if key == 'operations':
                for operation in data_model[key]:
                    if obj.__full_path__().replace("/", "") == '':
                        continue
                    method_name = data_model_path.replace("/", "_") + '_operations_' + operation
                    setattr(obj, operation, obj._wrapper.__getattribute__(method_name).__get__(obj))
                    setattr(getattr(obj, operation).__func__, '__name__', operation)
            setattr(obj, key, DataModelProxy(wrapper=obj._wrapper, name=key, path=obj.__full_path__(), model_path=obj.__data_model_path__()))
        for key in data_model:
            if not key.startswith("@") or ":" not in key:
                continue
            [fieldName, fieldValue] = key.split(":")
            fieldName = fieldName.replace("@", "")
            try:
                if obj._wrapper._get(obj.__full_path__()+"/"+fieldName) != fieldValue:
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
