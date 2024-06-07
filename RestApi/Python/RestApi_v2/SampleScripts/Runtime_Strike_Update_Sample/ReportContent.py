import sys, os, re, time
from Section import Section
from collections import defaultdict
from DifferenceReport import DifferenceReport
sys.path.append(os.path.dirname(__file__))
from restPyWrapper3 import *

class ReportContent:
    
    def __init__(self, bps, runId, security = False):
        self.content = {}
        self.bps = bps
        self.sections = []
        self.run_id = runId
        self.security_check = security
        
    def create_content(self):
        self.content = self.bps.reports.getReportContents(runid=self.run_id, getTableOfContents=True)
    
    def load_all_section(self):
        id_of_security_start = ""
        for i in range(len(self.content)):           
            id = self.content[i]["Section ID"]
            name = self.content[i]["Section Name"]    
            section_split = id.split(".")
            if len(section_split) > 1:
                parent_id = ".".join(id.split(".")[:-1])
                parent_section = self.retrieve_section_by_id(parent_id)
                if parent_section:
                    parent_section.children.append(id)
            section = Section(id,name,i)
            if id_of_security_start: 
                if id.startswith(id_of_security_start):
                    section.security = True
                    section.load_section()
                    section.normalize_variant_name()
            elif name == "Component Detection Assessment":
                id_of_security_start = id
            # Now all the security section children gets the detail of the table    
            self.sections.append(section)
    
    def retrieve_section_by_id(self, section_id):
        for section in self.sections:
            if section_id == section.id:
                return section
        return None
    
    def compare_reportContent(self, content_to_compare): #
        try:
            difference = DifferenceReport()
            for section in self.sections:
                section_to_compare = content_to_compare.find_diff_sections(section)
                if section_to_compare: # Same Name Security or not Security
                    
                    # Any difference in the exisiting list
                    if section.security and not section.children: # if it's a child
                        section.get_security_content(self.bps, self.run_id)  
                        if not section_to_compare.children and not section_to_compare.detail:      
                            difference.add_change(section.to_dict())
                        else:                           
                            if section.security_strike_total != section_to_compare.security_strike_total: 
                                section_diff = section.compare_security(section_to_compare,self.sections)
                                difference.add_change(section_diff)
                    else:
                        difference.add_change(section.to_dict())
                else: 
                    if section.security and not section.children: # if it's a child
                        section.get_security_content(self.bps, self.run_id)
                    difference.add_change(section.to_dict())
            difference.print_all(self.security_check)
        except Exception as err:
            raise Exception(str(err)) 
        
        
    def compare_raw_reportContent(self, content_to_compare): #    
        try:
            difference = DifferenceReport()
            for section in self.sections:
                if not content_to_compare.find_sections_by_name(section.name): # The name are totally different, new section found
                    # Any difference in the exisiting list
                        difference.add_raw_change(section) # if it's a security component, it will generate things from detail    
            difference.print_raw_all()      
        except Exception as err:
            raise Exception(str(err))         
        
    def find_diff_sections(self, section_to_compare):
        for section in self.sections:
            if section.security and section_to_compare.security:
                if section.relative_name == section_to_compare.relative_name:
                    return section
            else:
                if section.name == section_to_compare.name:
                    return section
        return None
        
        
    def find_sections_by_name(self, section_name):
        for section in self.sections:
            if section.name == section_name:
                return True
        return False