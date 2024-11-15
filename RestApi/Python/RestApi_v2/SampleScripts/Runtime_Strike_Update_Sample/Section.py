import re
import time
from collections import defaultdict

class Section:
    def __init__(self, id, name, index):
        self.id = id
        self.name = name
        self.relative_name = ""
        self.index = index
        self.security_strike_allow_blocks = -1
        self.security_strike_total = -1
        self.detail = []
        self.children = []
        self.security = False
    
    def compare_security(self, section_to_compare, sections):
        result = {}
        try:
            if self.security_strike_total != section_to_compare.security_strike_total: # total strike is different

                result["Section ID"] = self.id
                result["Section Name"] = self.relative_name
                result["Strike Total Difference"] = abs(section_to_compare.security_strike_total - self.security_strike_total)

                if self.children and not section_to_compare.children:# get the detail from children
                    
                    children_list = []
                    for id in self.children:
                        child = self.get_section_by_id(id,sections)
                        if child:
                            children_list.append(child)
                    result["Detail Difference"] = defaultdict(list)
                    latest_time = float(section_to_compare.detail[0]["Time of strike"][-1])
                    for child in children_list:
                        j = 0
                        while j < len(len(child.detail[0]["Time of strike"])):
                            if float(child.detail[0]["Time of strike"][i]) <= latest_time:
                                del child.detail[0]["Time of strike"][i]
                                del child.detail[1]["Strike Name"][i]
                                del child.detail[2]["Strike Result"][i]
                                del child.detail[3]["Strike Reference"][i]
                                del child.detail[4]["Permutations"][i]
                                del child.detail[5]["Strike Tuples"][i]
                            else:
                                j += 1   

                elif not self.children and not section_to_compare.children: # Both security child
                    result["Detail Difference"] = defaultdict(list)
                    latest_time = float(section_to_compare.detail[0]["Time of strike"][-1])
                    if self.detail[0]["Time of strike"]:
                        for i in range(len(self.detail[0]["Time of strike"])):
                            if float(self.detail[0]["Time of strike"][i]) > latest_time:
                                result["Detail Difference"]["Time of strike"].append(self.detail[0]["Time of strike"][i])
                                result["Detail Difference"]["Strike Name"].append(self.detail[1]["Strike Name"][i])    
                                result["Detail Difference"]["Strike Result"].append(self.detail[2]["Strike Result"][i]) 
                                result["Detail Difference"]["Strike Reference"].append(self.detail[3]["Strike Reference"][i])  
                                result["Detail Difference"]["Permutations"].append(self.detail[4]["Permutations"][i])  
                                result["Detail Difference"]["Strike Tuples"].append(self.detail[5]["Strike Tuples"][i])      
        except Exception as err:
            raise Exception(str(err))
        return result
             
    def get_security_content(self,bps,report_id):
        start = time.time()
        self.detail = bps.reports.getReportTable(report_id,sectionId=self.id)
        end = time.time()
        d_time = end -start
        print("It takes {0} s to complete.".format(d_time))
        return self.detail
    
    def get_section_by_id(self,section_id, sections):
        for section in sections:
            if section.id == section_id:
                return section
        return None
    
    def load_section(self):
        if self.security:
        # Regular expression pattern to match pairs of numbers separated by a "/"
            pattern = r'\b(\d+)/(\d+)\b'
            # Find all matches in the input string
            matches = re.findall(pattern, self.name)
            # Convert matches to list of tuples with integers
            if matches:
                self.security_strike_allow_blocks = int(matches[0][0])
                self.security_strike_total = int(matches[0][1])
                self.relative_name = self.name.replace(f" {self.security_strike_allow_blocks}/{self.security_strike_total}", "")
    
    def normalize_variant_name(self):
        if self.name:
            sep_name = self.name.split("/")
            if len(sep_name) > 3 and sep_name[0] == 'strikes':
                self.name = "/".join(sep_name[2:])
                self.relative_name = "/".join(self.relative_name.split("/")[2:])
            
    def to_dict(self):
        result = {}
        result["Section ID"] = self.id
        if self.relative_name:
            result["Section Name"] = self.relative_name
        else:
            result["Section Name"] = self.name
        if self.detail: 
            result["Strike Total Difference"] = self.security_strike_total
            result["Detail Difference"] = defaultdict(list)
            try:
                if self.detail[0]["Time of strike"]:
                    for i in range(len(self.detail[0]["Time of strike"])):
                        result["Detail Difference"]["Time of strike"].append(self.detail[0]["Time of strike"][i])
                        result["Detail Difference"]["Strike Name"].append(self.detail[1]["Strike Name"][i])    
                        result["Detail Difference"]["Strike Result"].append(self.detail[2]["Strike Result"][i]) 
                        result["Detail Difference"]["Strike Reference"].append(self.detail[3]["Strike Reference"][i])  
                        result["Detail Difference"]["Permutations"].append(self.detail[4]["Permutations"][i])  
                        result["Detail Difference"]["Strike Tuples"].append(self.detail[5]["Strike Tuples"][i]) 
            except Exception as err:
                raise Exception(str(err))
        return result
    
    def __repr__(self):
        return "Section(ID={0}, name={1})".format(self.id,self.name)
    
    def __str__(self):
        return "Section ID is {0}, the name is {1}".format(self.id,self.name)