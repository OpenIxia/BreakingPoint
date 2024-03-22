# Title:  Python Script made to exemplify how to merge 2 similar reports from two chassis 
# Actions:
#   1. Provide system info and report internal id
#   2. Provide section_path_of_interest with the report label sections 
# Output:
# will create a folder: report\<system1>_<testname1>_<id1>_<system2>_<test_name2>_<id2>
# 
#================

import sys, os
from datetime import datetime, timedelta
from collections import Counter
import traceback 
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(os.path.dirname(__file__)+"/libs/python")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
#bps system info
bps_system1  = '10.36.66.31'
bpsuser1     = 'admin'
bpspass1    = 'admin'
testid_1 = 17
 
bps_system2  = 'merpro2g.lbj.is.keysight.com'
bpsuser2     = 'admin'
bpspass2    = 'admin'
testid_2 = 3321

section_of_interest = ""
'''
works with interest section that has time,tx,rx layout
'''
section_ids_of_interes = []
section_path_of_interest = ["Detailed Summarized Statistics \ Interface (layer 1-2) \ [all] \ Megabits/s",\
                            "Detailed Summarized Statistics \ IP \ TCP Sessions",\
                            "Detailed Summarized Statistics \ IP \ TCP Sessions/s"]

########################################
class BPS_Test_Result:
    def __init__(self, bps, test_id):
        self.bps = bps
        self.test_id = test_id
        self.table_of_contents = bps.reports.getReportContents(runid=test_id, getTableOfContents=True)
        self.test_name = self.table_of_contents[0]['Section Name']
        self.start_time_str = ''
        self.start_time = ''
        self.execution_status = ''
        self.test_data_dict = {}
        self.sections_ids_of_intrest = []

        self.get_start_time()
        self.get_result_tables()
    
    def get_sections_ids_from_section_path(self, path_of_interest):
        id_candidate = []
        path_list = path_of_interest.split("\\")
        clean_section = path_list[-1].strip()
        
        for i in range(len(self.table_of_contents)):
            if clean_section == self.table_of_contents[i]["Section Name"]:
                id_candidate.append(self.table_of_contents[i]["Section ID"])
                
        # base conditions here
        if len(id_candidate) == 0:
            print("The target section cannot be found. Please check the input!")
            return None
        elif len(id_candidate) == 1:
            return id_candidate[0]
        elif len(id_candidate) > 1 and len(path_list) == 1:
            print("Duplicates result found in the provided section path of interest. Please check the input!")
            return None
        else:
            cur_path_list = "\\".join(path_list[:-1])
            # recursive search starts here
            unique_prefix = self.get_sections_ids_from_section_path(cur_path_list)
            if unique_prefix:
                result = [element for element in id_candidate if element.startswith(unique_prefix)]
                return result[0]
            else:
                return None  
    
    def get_start_time(self):
        results_with_same_name = self.bps.reports.search(searchString = 'quick_test',\
                                                      limit = 10000,\
                                                      sort = 'startTime',\
                                                      sortorder = 'descending')
        for result in results_with_same_name:
            if result['runid'] == self.test_id:
                self.start_time_str = result['startTime']
                #self.start_time = datetime.strptime(self.start_time_str, '%a %b %d %H:%M:%S %Z %Y')
                self.start_time =  parse_timestamp_with_timezone(self.start_time_str)
                self.execution_status = result['result']
                break

    def get_result_tables(self):
        #to do - get names
        for section_path in section_path_of_interest:
            section_id = self.get_sections_ids_from_section_path(section_path)
            tabledata = self.bps.reports.getReportTable(runid=self.test_id, sectionId=section_id)
            self.test_data_dict[section_id] = tabledata



def merge_results(result1, result2):
    deltaTime = result2.start_time.timestamp() - result1.start_time.timestamp()
    merged_test_data_dict = {}
    for section in result1.test_data_dict:
        merged_test_data_dict[section] = merge_table(result1.test_data_dict[section],\
                                                     result2.test_data_dict[section],\
                                                     deltaTime)

    return merged_test_data_dict       

def merge_table(table1_dict, table2_dict, deltaTime):
    merged_table = {}
    #convert report  time indexes to flost from string
    table1_dict[0]['time'] = [float(x) for x in table1_dict[0]['time']]
    table2_dict[0]['time'] = [float(x) for x in table2_dict[0]['time']]
    time_series1  = table1_dict[0]['time']
    time_series2  = table2_dict[0]['time']
    #adjust based on deltatime- if second chassis starts later some values will be negative
    time_series2 = [x + deltaTime for x in time_series2]
    time_series_r = merge_poll_time(time_series1, time_series2)
    index_time_series1 = -1
    index_time_series2 = -1
    merged_table ['time'] = []
    for pooltime in time_series_r:
        try: 
            index_time_series2= time_series2.index(pooltime)
        except: 
            pass
        try: 
            index_time_series1= time_series1.index(pooltime)
        except: 
            pass
        merged_table ['time'].append(pooltime)
        for column_index in range(len(table1_dict[1:])):
            name = list(table1_dict[1+column_index].keys())[0]
            if name not in merged_table:
                merged_table[name] = []
            merged_table[name].append(get_agg_value(index_time_series1, index_time_series2, \
                                                table1_dict[1+column_index][name],
                                                table2_dict[1+column_index][name] ) 
                                    )
    return merged_table

def get_agg_value (ix1, ix2, list1, list2):
    val1 = 0
    val2 = 0
    if ix1 > 0 :
        val1 = list1[ix1]
    if ix2 > 0 :
        val2 = list2[ix2]
    try:
        result = float(val1)+float(val2)
    except:
        result = f"{val1} + {val2}" 
    return result


def parse_timestamp_with_timezone(timestamp_string):
    #move UTC to PDT as it is currenly worng set
    timestamp_string = timestamp_string.replace('UTC', 'PDT')
    timezone_offsets = {
    'PDT': timedelta(hours=-7),  # Pacific Daylight Time (UTC-7) - should be -7 haked to be 0 as chasis not in same TZ
    }
    parts = timestamp_string.split()
    # Convert timezone abbreviation to UTC offset
    timezone_offset = timezone_offsets.get(parts[-2], timedelta(0))
    # Remove the timezone abbreviation from the parts
    del parts[-2]
    # Reconstruct the modified timestamp string
    timestamp_string = ' '.join(parts)
    # Parse the timestamp string into a datetime object
    #return datetime.strptime(timestamp_string, '%a %b %d %H:%M:%S %Y') + timezone_offset
    return datetime.strptime(timestamp_string, '%a %b %d %H:%M:%S %Y')


def merge_poll_time(list1, list2):
    # Count occurrences of elements in both lists
    counts = Counter(list1 + list2)
    # Construct the list of unique elements sorted
    sorted_unique_elements = sorted(counts.keys())
    return sorted_unique_elements

def write_csvs(result_dict, results_path):
    #create folder
    folder_path = os.path.join('report', results_path)
    if not os.path.exists(folder_path):
         os.makedirs(folder_path)

    print("Writing to CSV file..")
    for table in result_dict:
        with open(os.path.join(folder_path,f"{table}.csv"), "w") as file:
            tdict= result_dict[table]
            col_names =list(tdict.keys())
            file.write(",".join(col_names) + "\n")
            for index in range(len(tdict['time'])):
                row_values = [str(tdict[column][index]) for column in tdict]
                file.write(",".join(row_values) + "\n")
                

# Login to BPS systems and extract the csv reports
if __name__ == '__main__':
    bps1 = BPS(bps_system1, bpsuser1, bpspass1, checkVersion=False)
    bps1.login()
    bps2 = BPS(bps_system2, bpsuser2, bpspass2, checkVersion=False)
    bps2.login()
    try:
        result1 = BPS_Test_Result(bps1,test_id= testid_1)
        result2 = BPS_Test_Result(bps2,test_id= testid_2)

        result_dict = merge_results(result1, result2)
        results_path = f"{bps_system1}_{result1.test_name}_{result1.test_id}_{bps_system2}_{result2.test_name}_{result2.test_id}"
        write_csvs(result_dict, results_path)
        print("Completed.")
    except Exception as err:
        print (str(err) )
        traceback.print_exc()

    ########################################
    print("Session logout")
    bps1.logout()
    bps2.logout()

    