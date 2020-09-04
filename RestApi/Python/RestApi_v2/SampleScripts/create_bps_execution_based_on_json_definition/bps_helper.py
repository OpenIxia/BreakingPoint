import sys, os, time, json, re
import json
# from .bps_helper import *
from bps import BPS


tls_ciphers = {"TLS_VERSION_3_3": ["TLS_CIPHERSUITE_C031", "TLS_CIPHERSUITE_C032", "TLS_CIPHERSUITE_C02B", "TLS_CIPHERSUITE_C02C", "TLS_CIPHERSUITE_009C", "TLS_CIPHERSUITE_009D"],
               "TLS_VERSION_3_4": ["TLS_CIPHERSUITE_1302", "TLS_CIPHERSUITE_1301", "TLS_CIPHERSUITE_1303"]}

tls_name = {"TLS_VERSION_3_3": "TLSv1.2", "TLS_VERSION_3_4": "TLSv1.3"}
cipher_name = {"TLS_CIPHERSUITE_C031": "ECDHE-RSA- AES128-GCM-SHA256",
               "TLS_CIPHERSUITE_C032": "ECDHE-RSA- AES256-GCM-SHA384",
               "TLS_CIPHERSUITE_C02B": "ECDHE-ECDSA-AES128-GCM-SHA256",
               "TLS_CIPHERSUITE_C02C": "ECDHE-ECDSA- AES256-GCM-SHA384",
               "TLS_CIPHERSUITE_009C": "(RSA)AES128-GCM-SHA256",
               "TLS_CIPHERSUITE_009D": "(RSA) AES256-GCM-SHA384",
               "TLS_CIPHERSUITE_1302": "TLS_AES_256_GCM_SHA384 (TLSv1.3)",
               "TLS_CIPHERSUITE_1301": "TLS_AES_128_GCM_SHA256 (TLSv1.3)",
               "TLS_CIPHERSUITE_1303": "TLS_CHACHA20_POLY1305_SHA256(TLSv1.3)",
               "TLS_CIPHERSUITE_C02F" : "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
               "TLS_CIPHERSUITE_NONE": "none"}
cipher_tags = {val: cipher for cipher, val in cipher_name.items()}


class BPS_Helper(object):
    def __init__(self, bps_object=None, json_data=None, test_name=None):
        if not bps_object:
            raise ValueError("BPS object not provided")
        self.__bps_conn__ = bps_object
        if not json_data:
            raise ValueError("Data for creating applications not provided")
        with open(json_data) as json_file:
            data = json.load(json_file)
        self.app_data = data
        self.protocols = list()
        self.protocol_flows = dict()
        self.superflow_names = list()
        self.weights = list()
        self.app_profile_name = None
        self.__get_all_protocols__()
        if test_name is None:
            self.name_given = False
            self.test_name = "nso_app"
            for proto in self.protocols:
                self.test_name = self.test_name + "_" + proto
        else:
            self.test_name = test_name
            self.name_given = True

    def create_application_profile(self):
        flow_list = list()
        self.app_profile_name = str()
        for name in self.superflow_names:
            self.app_profile_name = self.app_profile_name + name
        self.__bps_conn__.appProfile.new()
        i = 0
        for flow in self.superflow_names:
            flow_list.append({"superflow": str(flow), "weight": str(self.weights[i])})
            i += 1

        self.__bps_conn__.appProfile.add(flow_list)

        self.__bps_conn__.appProfile.saveAs(self.app_profile_name, force=True)
        print("Saved application profile with the name: " + self.app_profile_name)

        # self.__bps_conn__

    def create_nso_testmodel(self):
        component1_name = "NSO_appsim_1"
        component2_name = "NSO_appsim_2"
        self.__bps_conn__.testmodel.new()
        self.__bps_conn__.testmodel.add(name=component1_name, type='appsim', active=True, component='appsim')
        self.__bps_conn__.testmodel.add(name=component2_name, type='appsim', active=True, component='appsim')
        id1 = self.__bps_conn__.testmodel.component.get()[0]['id']
        id2 = self.__bps_conn__.testmodel.component.get()[1]['id']
        profile_name = {"profile": str(self.app_profile_name)}
        self.__bps_conn__.testmodel.component[id1].patch(profile_name)
        self.__bps_conn__.testmodel.component[id2].patch(profile_name)
        self.__bps_conn__.testmodel.saveAs(self.test_name, force=True)
        print("Saved test model with the name: " + self.test_name)

    def __get_all_protocols__(self):
        if self.app_data['protocolMix']:
            pass
        else:
            raise ValueError("Key 'ProtocolMix not found in JSON data")
        for protocol in self.app_data['protocolMix'].keys():
            self.protocols.append(protocol)
            self.weights.append(self.app_data['protocolMix'][str(protocol)]['percentage'])
            self.protocol_flows[protocol] = self.app_data['protocolMix'][protocol]

    def __set_server_hostname__(self):
        self.__bps_conn__.superflow.hosts["Server"].hostname.set("NetSecOpen.com")
        self.__bps_conn__.superflow.hosts["Server"].iface.set("target")

    def __add_http_flows__(self, data, protocol):
        def check_key(key, check):
            if str(key) in check.keys():
                return True
            else:
                return False

        # self.__bps_conn__.superflow.addFlow({"name": "httpadv", "to": "Server", "from": "Client"})
        self.__bps_conn__.superflow.addAction(flowid=1, type="get_uri", actionid=1, source="client")
        self.__bps_conn__.superflow.actions["1"].patch({"uri": "/index.html"})
        self.__bps_conn__.superflow.addAction(flowid=1, type="response_ok", actionid=2, source="server")
        # self.__bps_conn__.superflow.addAction(flowid=1, type="goto", actionid=3, source="server")
        self.__bps_conn__.superflow.actions["2"].patch({"transflag": ("end" if self.protocol_flows[protocol]['Config']['Server']['CloseMethod'] == "FIN" else "")})
        self.__bps_conn__.superflow.addAction(flowid=1, type="goto", actionid=3, source="client")
        self.__bps_conn__.superflow.actions["3"].patch(
            {"transflag": "startend", "iteration": self.protocol_flows[str(protocol)]["requestsPerConnection"]})
        self.__bps_conn__.superflow.actions["1"].patch({"user-agent": (self.protocol_flows[protocol]['Config']['Client']['Headers']['User-Agent'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['User-Agent'] else "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
                                                        "label": (self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] if self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] else "GET"),
                                                        "method": (self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] if self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] else "GET"),
                                                        "accept": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][0]['Accept'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][0]['Accept'] else "*/*"),
                                                        "accept-language": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][1]['Accept-Language'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][1]['Accept-Language'] else "en-us"),
                                                        "accept-encoding": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][2]['Accept-Encoding'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][2]['Accept-Encoding'] else "gzip, deflate, compress")})
        self.__bps_conn__.superflow.actions["2"].patch({"method": "200",
                                                        "accept": "*/*",
                                                        "accept-language": "en-us",
                                                        "accept-encoding": "gzip, deflate, compress",
                                                        # "Port": "80",
                                                        "defTxnProfile": (self.protocol_flows[protocol]['Config']['Server']['defTxnProfile'] if self.protocol_flows[protocol]['Config']['Server']['defTxnProfile'] else "transaction profile"),
                                                        "cookieExpiresDateTime": (self.protocol_flows[protocol]['Config']['Server']['cookieExpiresDateTime'] if self.protocol_flows[protocol]['Config']['Server']['cookieExpiresDateTime'] else "Mon, 05 Jan 1970 00:00:00 GMT"),
                                                        "serverType": (self.protocol_flows[protocol]['Config']['Server']['serverType'] if self.protocol_flows[protocol]['Config']['Server']['serverType'] else "Microsoft-IIS/8.5")
                                                        })
        self.__bps_conn__.superflow.actions["2"].patch({"content-type": ("text/ascii charset=utf-8" if self.protocol_flows[protocol]['Config']['TransactionProfiles']['bodyType'] == "ascii" else ""),
                                                        "response-data-generated": "html",
                                                        "response-rand-max": (self.protocol_flows[protocol]['Config']['TransactionProfiles']['bodyBytes'] if self.protocol_flows[protocol]['Config']['TransactionProfiles']['bodyBytes'] else "1000"),
                                                        "response-rand-min": (self.protocol_flows[protocol]['Config']['TransactionProfiles']['bodyBytes'] if self.protocol_flows[protocol]['Config']['TransactionProfiles']['bodyBytes'] else "1000")
                                                        })

        self.__set_server_hostname__()
        # pass

    def __add_https_flows__(self, data, protocol):
        general_tls_settings = {}

        def check_key(key, check):
            if str(key) in check.keys():
                return True
            else:
                return False

        self.__bps_conn__.superflow.addAction(flowid=1, type="tls_accept", actionid=1, source="server")
        self.__bps_conn__.superflow.addAction(flowid=1, type="tls_start", actionid=2, source="client")
        self.__bps_conn__.superflow.addAction(flowid=1, type="get_uri", actionid=3, source="client")
        self.__bps_conn__.superflow.actions["3"].patch({"uri": "/index.html"})
        self.__bps_conn__.superflow.addAction(flowid=1, type="response_ok", actionid=4, source="server")
        self.__bps_conn__.superflow.actions["4"].patch({"transflag": ("end" if self.protocol_flows[protocol]['Config']['Server']['CloseMethod'] == "FIN" else "")})
        self.__bps_conn__.superflow.addAction(flowid=1, type="goto", actionid=5, source="client")
        self.__bps_conn__.superflow.actions["5"].patch(
            {"transflag": "startend", "iteration": data["Client"]["requestsPerConnection"]})
        self.__bps_conn__.superflow.actions["1"].patch({"tls_ciphers": "TLS_CIPHERSUITE_C02F",
                                                        "tls_ciphers2": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers3": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers4": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers5": "TLS_CIPHERSUITE_NONE",
                                                        # "label": "GET",
                                                        "tls_max_version": "TLS_VERSION_3_3",
                                                        "tls_min_version": "TLS_VERSION_3_3",
                                                        "tls_handshake_timeout": "4294967295",
                                                        "tls_decrypt_mode": "L4_TLS_DECRYPT_MODE_DECRYPT"})
        self.__bps_conn__.superflow.actions["2"].patch({"tls_ciphers": "TLS_CIPHERSUITE_C02F",
                                                        "tls_ciphers2": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers3": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers4": "TLS_CIPHERSUITE_NONE",
                                                        "tls_ciphers5": "TLS_CIPHERSUITE_NONE",
                                                        # "label": "GET",
                                                        "tls_max_version": "TLS_VERSION_3_3",
                                                        "tls_min_version": "TLS_VERSION_3_3",
                                                        "tls_handshake_timeout": "4294967295",
                                                        "tls_decrypt_mode": "L4_TLS_DECRYPT_MODE_DECRYPT"})
        self.__bps_conn__.superflow.actions["3"].patch({"user-agent": (self.protocol_flows[protocol]['Config']['Client']['Headers']['User-Agent'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['User-Agent'] else "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"),
                                                        "label": (self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] if self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] else "GET"),
                                                        "method": (self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] if self.protocol_flows[protocol]['Config']['Client']['command'].split()[0] else "GET"),
                                                        "accept": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][0]['Accept'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][0]['Accept'] else "*/*"),
                                                        "accept-language": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][1]['Accept-Language'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][1]['Accept-Language'] else "en-us"),
                                                        "accept-encoding": (self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][2]['Accept-Encoding'] if self.protocol_flows[protocol]['Config']['Client']['Headers']['ExtendedHeaders'][2]['Accept-Encoding'] else "gzip, deflate, compress")})
        self.__bps_conn__.superflow.actions["4"].patch({"method": "200",
                                                        "accept": "*/*",
                                                        "accept-language": "en-us",
                                                        "accept-encoding": "gzip, deflate, compress",
                                                        # "Port": "80",
                                                        "defTxnProfile": (self.protocol_flows[protocol]['Config']['Server']['defTxnProfile'] if self.protocol_flows[protocol]['Config']['Server']['defTxnProfile'] else "transaction profile"),
                                                        "cookieExpiresDateTime": (self.protocol_flows[protocol]['Config']['Server']['cookieExpiresDateTime'] if self.protocol_flows[protocol]['Config']['Server']['cookieExpiresDateTime'] else "Mon, 05 Jan 1970 00:00:00 GMT"),
                                                        "serverType": (self.protocol_flows[protocol]['Config']['Server']['serverType'] if self.protocol_flows[protocol]['Config']['Server']['serverType'] else "Microsoft-IIS/8.5"),
                                                        "content-type": ("text/ascii charset=utf-8" if
                                                                         self.protocol_flows[protocol]['Config'][
                                                                             'TransactionProfiles'][
                                                                             'bodyType'] == "ascii" else ""),
                                                        "response-data-generated": "html",
                                                        "response-rand-max": (self.protocol_flows[protocol]['Config'][
                                                                                  'TransactionProfiles']['bodyBytes'] if
                                                                              self.protocol_flows[protocol]['Config'][
                                                                                  'TransactionProfiles'][
                                                                                  'bodyBytes'] else "1000"),
                                                        "response-rand-min": (self.protocol_flows[protocol]['Config'][
                                                                                  'TransactionProfiles']['bodyBytes'] if
                                                                              self.protocol_flows[protocol]['Config'][
                                                                                  'TransactionProfiles'][
                                                                                  'bodyBytes'] else "1000")
                                                        })

    def __add_flows_to_superflow__(self, flow_data, protocol):
        if "Client" not in flow_data.keys():
            raise ValueError("Could not find 'Client' flows in JSON file.")
        if "Server" not in flow_data.keys():
            raise ValueError("Could not find 'Server' flows in JSON file.")
        client_data = flow_data['Client']
        server_data = flow_data['Server']
        # if re.search('HTTP', str(protocol)):
        if (str(protocol) == "HTTP") or (str(protocol) == "http"):
            self.__bps_conn__.superflow.addFlow({"name": "httpadv", "to": "Server", "from": "Client"})
            self.__add_http_flows__(flow_data, "HTTP")
        # if re.search('HTTPS', str(protocol)):
        if (str(protocol) == "HTTPS") or (str(protocol) == "https"):
            self.__bps_conn__.superflow.addFlow({"name": 'httpadv', "to": "Server", "from": "Client"})
            self.__add_https_flows__(flow_data, "HTTPS")

    def create_superflow(self):
        name_one = 'nso_sf_'
        # name_two = 'test_2'
        for protocol in self.protocols:
            self.__bps_conn__.superflow.new()
            if 'percentage' not in self.protocol_flows[protocol].keys():
                print("Could not find 'percentage' weight in the JSON file. Setting to default")
            else:
                self.__bps_conn__.superflow.weight.set(
                    int(self.protocol_flows[protocol]['percentage']))
            # self.__bps_conn__.superflow.percentBandwidth.set(int())
            print("Adding flows to superflow ")
            if "Config" not in self.protocol_flows[protocol].keys():
                raise ValueError("Could not find 'Config' in the JSON file to add flows. Setting to default")
            else:
                self.__add_flows_to_superflow__(self.protocol_flows[protocol]['Config'], protocol)
            if (str(protocol) == "HTTP") or (str(protocol) == "http"):
                sf_name = str(str(name_one + str(protocol) + "_v" + (self.protocol_flows[protocol]["version"]).replace(".", "") + "_" + self.protocol_flows[protocol]["Config"]["TransactionProfiles"]["bodyBytes"] + "b_req" + self.protocol_flows[protocol]["requestsPerConnection"]))
                self.__bps_conn__.superflow.saveAs(name=sf_name, force=True)
                print("Saved superflow as: " + sf_name)
                self.superflow_names.append(sf_name)
            elif (str(protocol) == "HTTPS") or (str(protocol) == "https"):
                sf_name_https = str(name_one + str(protocol) + "_tls" + self.protocol_flows[protocol]["tlsConfig"]["tlsVersion"].replace(".", "") + "_" + self.protocol_flows[protocol]["tlsConfig"]["cipher"] +"_v" + (self.protocol_flows[protocol]["version"]).replace(".", "") + "_" + self.protocol_flows[protocol]["Config"]["TransactionProfiles"]["bodyBytes"] + "b_req" + self.protocol_flows[protocol]["requestsPerConnection"])
                self.__bps_conn__.superflow.saveAs(name=sf_name_https, force=True)
                print("Saved superflow as: " + sf_name_https)
                self.superflow_names.append(sf_name_https)
            # self.superflow_names.append(str(name_one + str(protocol)))


if __name__ == '__main__':
    file = r'C:\REST_BPS\QA\regression\auto\pythar\rest\REST_Comp_Sanity\test.AppSim_NATchecked\bps_helper\http_smtp_mix-13052020_Test1.json'
    bps_system = '10.36.81.89'
    bpsuser = 'admin'
    bpspass = 'admin'
    bps = BPS(bps_system, bpsuser, bpspass)
    bps.login()
    bps_create = BPS_Helper(bps_object=bps, json_data=file)
    bps_create.create_superflow()
    bps_create.create_application_profile()
    bps_create.create_nso_testmodel()