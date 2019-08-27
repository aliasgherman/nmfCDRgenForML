import os
import numpy as np
from datetime import time, datetime
import pandas as pd
import io

class StatsGenerator:
    def __init__(self, filename, NEWLINE):
        self.filename = filename
        self.NEWLINE = NEWLINE
        self.results = {}
        self.min_time = datetime.max.time()
        self.max_time = datetime.min.time()
        self.start_date = datetime.max.date()
        self.stop_date = datetime.min.date()
        self.fileformat = -1


    def print_results(self):
        headers = ["Filename", "FileFormat", "NEWLINE", "StartDate", "StartTime", "StopDate", "StopTime"]
        values = [self.filename, self.fileformat, self.NEWLINE, self.start_date, self.min_time, self.stop_date, self.max_time]
        res = dict(zip(headers,values))
        self.results.update(res)
        print(self.results)

    def run(self):
        print("Inside the stats generator module.", self.filename)
        if os.path.isfile(self.filename):
            try:
                with io.open(self.filename, "r", newline=self.NEWLINE) as f:
                    currline = f.readline().upper()
                    while currline and currline.strip() != "":
                        lb = currline.split(",")
                        if len(lb) < 3:
                            print("Unexpected line. Breaking stats generation. ", currline)
                            return {} #return an empty dict as file may be damaged or not a NMF file

                        ##########################################################
                        if lb[0] in self.results.keys():
                            self.results[lb[0]] = self.results[lb[0]] + 1
                        else:
                            self.results[lb[0]] = 1
                        ##########################################################

                        ##########################################################
                        if lb[0] == "#START":
                            self.start_date = datetime.strptime(lb[3].strip().replace('"', ''), "%d.%m.%Y").date()
                            self.min_time = datetime.strptime(lb[1].split(".")[0], "%H:%M:%S").time()
                        elif lb[0] == "#FF":
                            self.fileformat = lb[3].strip()
                        elif lb[0] == "#STOP":
                            self.stop_date = datetime.strptime(lb[3].strip().replace('"', ''), "%d.%m.%Y").date()
                            self.max_time = datetime.strptime(lb[1].split(".")[0], "%H:%M:%S").time()
                        ##########################################################

                        ##########################################################
                        #This should be the last line in this loop (while currline)
                        currline = f.readline().upper()
                        ##########################################################

                print("File processed. Returning the results as a dictionary now. ")
                self.print_results()
                df = pd.DataFrame.from_dict(self.results, orient='index').reset_index()
                df.columns = ["OBJECT", "COUNT"]
                fpath, fname = os.path.split(self.filename)
                df.to_csv(os.path.join(fpath , "statsgen_" + fname + ".csv" ) )
                return self.results
            except Exception as e:
                print("An exception ocurred while reading the file. ", e)

