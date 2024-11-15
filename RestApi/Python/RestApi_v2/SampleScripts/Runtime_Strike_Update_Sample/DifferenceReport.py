from collections import defaultdict

class DifferenceReport:
    
    def __init__(self):
        self.sections = [] # -> dict {Section ID, Section Name, Strike Total Difference, Detail Difference[Time of Strike, Strike Name, Strike Reference, Permutations, Strike Tuples]}
        self.raw_sections = []
    def add_change(self,section):
        self.sections.append(section)  
    
    def add_raw_change(self,raw_section):
        self.raw_sections.append(raw_section)  
    
    def print_all(self, security):
        print("Differences:")
        if security:
             with open("checkResult.txt", "w") as file:
                for section in self.sections:
                    if "Strike Total Difference" in section and "Detail Difference" in section:
                        section_id = section["Section ID"]
                        section_name = section["Section Name"]
                        file.write("Section ID: {0}\n".format(section_id))
                        file.write("Section Name: {0}\n".format(section_name))
                        print("Section ID: {0}".format(section_id))
                        print("Section Name: {0}".format(section_name))
                        file.write("Strike Total Difference: {0}\n".format(section["Strike Total Difference"]))
                        print("Strike Total Difference: {0}\n".format(section["Strike Total Difference"]))
                        for i in range(len(section["Detail Difference"]["Time of strike"])):
                            file.write("Time of Strike: {0}\n".format(section["Detail Difference"]["Time of strike"][i]))
                            file.write("Strike Name: {0}\n".format(section["Detail Difference"]["Strike Name"][i]))
                            file.write("Strike Result: {0}\n".format(section["Detail Difference"]["Strike Result"][i]))
                            file.write("Strike Reference: {0}\n".format(section["Detail Difference"]["Strike Reference"][i]))
                            file.write("Permutations: {0}\n".format(section["Detail Difference"]["Permutations"][i]))
                            file.write("Strike Tuples: {0}\n".format(section["Detail Difference"]["Strike Tuples"][i]))
                            #print
                            print("Time of Strike: {0}\n".format(section["Detail Difference"]["Time of strike"][i]))
                            print("Strike Name: {0}\n".format(section["Detail Difference"]["Strike Name"][i]))
                            print("Strike Result: {0}\n".format(section["Detail Difference"]["Strike Result"][i]))
                            print("Strike Reference: {0}\n".format(section["Detail Difference"]["Strike Reference"][i]))
                            print("Permutations: {0}\n".format(section["Detail Difference"]["Permutations"][i]))
                            print("Strike Tuples: {0}\n".format(section["Detail Difference"]["Strike Tuples"][i]))
                            print("++++++++++++++++++++++++++++++++++++")
                            file.write("++++++++++++++++++++++++++++++++++++\n")
                file.write("===============================================================\n")
                print("===============================================================")
        else: 
            with open("checkResult.txt", "w") as file:
                for section in self.sections:
                    section_id = section["Section ID"]
                    section_name = section["Section Name"]
                    file.write("Section ID: {0}\n".format(section_id))
                    file.write("Section Name: {0}\n".format(section_name))
                    print("Section ID: {0}".format(section_id))
                    print("Section Name: {0}".format(section_name))
                    if "Strike Total Difference" in section and "Detail Difference" in section:
                        file.write("Strike Total Difference: {0}\n".format(section["Strike Total Difference"]))
                        print("Strike Total Difference: {0}\n".format(section["Strike Total Difference"]))
                        for i in range(len(section["Detail Difference"]["Time of strike"])):
                            file.write("Time of Strike: {0}\n".format(section["Detail Difference"]["Time of strike"][i]))
                            file.write("Strike Name: {0}\n".format(section["Detail Difference"]["Strike Name"][i]))
                            file.write("Strike Result: {0}\n".format(section["Detail Difference"]["Strike Result"][i]))
                            file.write("Strike Reference: {0}\n".format(section["Detail Difference"]["Strike Reference"][i]))
                            file.write("Permutations: {0}\n".format(section["Detail Difference"]["Permutations"][i]))
                            file.write("Strike Tuples: {0}\n".format(section["Detail Difference"]["Strike Tuples"][i]))
                            #print
                            print("Time of Strike: {0}\n".format(section["Detail Difference"]["Time of strike"][i]))
                            print("Strike Name: {0}\n".format(section["Detail Difference"]["Strike Name"][i]))
                            print("Strike Result: {0}\n".format(section["Detail Difference"]["Strike Result"][i]))
                            print("Strike Reference: {0}\n".format(section["Detail Difference"]["Strike Reference"][i]))
                            print("Permutations: {0}\n".format(section["Detail Difference"]["Permutations"][i]))
                            print("Strike Tuples: {0}\n".format(section["Detail Difference"]["Strike Tuples"][i]))
                            print("++++++++++++++++++++++++++++++++++++")
                            file.write("++++++++++++++++++++++++++++++++++++\n")
                file.write("===============================================================\n")
                print("===============================================================")
        
    def print_raw_all(self):
        print("Difference: ")
        with open ("checkResult.txt", "a+") as file:
            for raw_section in self.raw_sections:
                print("Section ID: {0}".format(raw_section.id))
                print("Section Name: {0}".format(raw_section.name))
                file.write("Section ID: {0}\n".format(raw_section.id))
                file.write("Section Name: {0}\n".format("Section Name: {0}".format(raw_section.name)))
                
                
    