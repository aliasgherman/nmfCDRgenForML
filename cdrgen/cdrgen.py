import os
import numpy as np
from datetime import time, datetime
import pandas as pd
from parsers import gps, cmdreq, cellmeas
import io

class CDRGenerator:
    def __init__(self, filename, NEWLINE):
        self.filename = filename
        self.NEWLINE = NEWLINE
        self.results = []
        self.min_time = datetime.max.time()
        self.max_time = datetime.min.time()
        self.start_date = datetime.max.date()
        self.stop_date = datetime.min.date()
        self.fileformat = -1
        self.clearcdr()

    def clearcdr(self):
        self.cdr = {"LAT" : None,
                    "LON" : None,
                    cellmeas.F_CELLMEASSYS : None}

        self.lastcdr = self.cdr

    def getFirstCdr(self):
        return {"INITIAL_" + str(i):j for i,j in self.cdr.items()}

    def getLastCdr(self):
        return {"FINAL_" + str(i):j for i,j in self.lastcdr.items()}


    def run(self):
        print("Inside the cdr generator module.", self.filename)
        if os.path.isfile(self.filename):
            try:
                with io.open(self.filename, "r", newline=self.NEWLINE) as f:
                    currline = f.readline().upper()
                    while currline and currline.strip() != "":
                        lb = currline.split(",")
                        if len(lb) < 3:
                            print("Unexpected line. Breaking cdr generation. ", currline)
                            return {} #return an empty dict as file may be damaged or not a NMF file

                        ##########################################################
                        if lb[0] == "#START":
                            self.start_date = datetime.strptime(lb[3].strip().replace('"', ''), "%d.%m.%Y").date()
                            self.min_time = datetime.strptime(lb[1].split(".")[0], "%H:%M:%S").time()
                        elif lb[0] == "#FF":
                            self.fileformat = int(lb[3].replace('"',"").replace(".","").strip())
                        elif lb[0] == "#STOP":
                            self.stop_date = datetime.strptime(lb[3].strip().replace('"', ''), "%d.%m.%Y").date()
                            self.max_time = datetime.strptime(lb[1].split(".")[0], "%H:%M:%S").time()
                        elif lb[0] == "CMDREQ": #this is beginning of a script command
                            self.clearcdr()
                            cmdRes = cmdreq.parseline(lb, self.fileformat)
                            self.cdr[cmdreq.F_CMDREQCMDNAME] = cmdRes[cmdreq.F_CMDREQCMDNAME]
                            #self.cdr[cmdreq.F_CMDREQCMDARG] = cmdRes[cmdreq.F_CMDREQCMDARG]
                            self.cdr[cmdreq.F_CMDREQINDEX] = cmdRes[cmdreq.F_CMDREQINDEX]
                        elif lb[0] == "GPS":
                            gpsRes = gps.parseline(lb, self.fileformat)
                            if self.cdr["LON"] == None:
                                self.cdr["LON"] = gpsRes[gps.F_GPSLON]
                                self.cdr["LAT"] = gpsRes[gps.F_GPSLAT]
                                self.cdr["SATELLITES"] = gpsRes[gps.F_GPSSATELLITE]
                            else:
                                self.lastcdr["LON"] = gpsRes[gps.F_GPSLON]
                                self.lastcdr["LAT"] = gpsRes[gps.F_GPSLAT]
                                self.lastcdr["SATELLITES"] = gpsRes[gps.F_GPSSATELLITE]

                        elif lb[0] == "CELLMEAS":
                            if self.cdr[cellmeas.F_CELLMEASSYS] == None:
                                self.cdr.update(cellmeas.parseline(lb, self.fileformat))
                            else:
                                self.lastcdr.update(cellmeas.parseline(lb, self.fileformat))


                        elif lb[0] == "CMDCOMP":
                            #print(self.cdr)
                            self.results.append(self.getFirstCdr())
                            self.results.append(self.getLastCdr())
                            self.clearcdr()

                        ##########################################################

                        ##########################################################
                        #This should be the last line in this loop (while currline)
                        currline = f.readline().upper()
                        ##########################################################

                print("File processed. Returning the results as a dictionary now. ")
                print(self.results)
                return self.results
            except Exception as e:
                print("An exception ocurred while reading the file. ", e)

