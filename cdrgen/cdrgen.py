import os
import numpy as np
from datetime import time, datetime
import pandas as pd
from parsers import gps, cmdreq, cellmeas, cqi, pdcprated, pdcprateu, plaid, plaiu
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
        self.pdcpD_AvgThp = []
        self.pdcpU_AvgThp = []
        self.cqiVals = []

    def getFirstCdr(self):
        return {"INITIAL_" + str(i):j for i,j in self.cdr.items()}

    def getLastCdr(self):
        return {"FINAL_" + str(i):j for i,j in self.lastcdr.items()}


    def run(self):
        print("Inside the cdr generator module.", self.filename)
        if os.path.isfile(self.filename):
            #try:
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
                        currRes = {}
                        currRes.update(self.getFirstCdr())
                        currRes.update(self.getLastCdr())
                        if len(self.cqiVals) == 0:
                            self.cqiVals = [np.nan] #to remove errors of empty list on np.nanmax

                        #print(self.cqiVals)
                        moreInfo = {"AVG_PDCP_DL_THROUGHPUT" : np.nanmean(self.pdcpD_AvgThp),
                                    "P90_PDCP_DL_THROUGHPUT" : np.nanpercentile(self.pdcpD_AvgThp, 90),
                                    "P10_PDCP_DL_THROUGHPUT" : np.nanpercentile(self.pdcpD_AvgThp, 10),
                                    "AVG_PDCP_UL_THROUGHPUT" : np.nanmean(self.pdcpU_AvgThp),
                                    "P90_PDCP_UL_THROUGHPUT" : np.nanpercentile(self.pdcpU_AvgThp, 90),
                                    "P10_PDCP_UL_THROUGHPUT" : np.nanpercentile(self.pdcpU_AvgThp, 10),
                                    "SESSION_MEAN_CQI" : np.nanmean(self.cqiVals),
                                    "SESSION_MEDIAN_CQI" : np.nanmedian(self.cqiVals),
                                    "SESSION_MAX_CQI" : np.nanmax(self.cqiVals),
                                    "SESSION_MIN_CQI" : np.nanmin(self.cqiVals)
                                    }
                        currRes.update(moreInfo)

                        self.results.append(currRes)

                        self.clearcdr()

                    elif lb[0] == "CQI":
                        cqiRes = cqi.parseline(lb, self.fileformat)
                        availHeaders = [x for x in cqiRes.keys() if x in cqi.F_CQIHEADERS]
                        CQIVALS = [cqiRes[x] for x in availHeaders]
                        CQI_MEANS = np.nanmean(CQIVALS)
                        CQI_MEDIANS = np.nanmedian(CQIVALS)
                        if self.cdr["LON"] == None:
                            self.cqiVals = CQIVALS
                            self.cdr["MEAN_CQI"] = CQI_MEANS
                            self.cdr["MEDIAN_CQI"] = CQI_MEDIANS
                            self.cdr.update(cqiRes)
                        else:
                            self.cqiVals.extend(CQIVALS)
                            self.lastcdr["MEAN_CQI"] = CQI_MEANS
                            self.lastcdr["MEDIAN_CQI"] = CQI_MEDIANS
                            self.lastcdr.update(cqiRes)

                    elif lb[0] == "PDCPRATED":
                        pdcpdrateRes = pdcprated.parseline(lb)
                        if self.cdr["LON"] == None:
                            self.cdr.update(pdcpdrateRes)
                            self.pdcpD_AvgThp = [pdcpdrateRes["PDCP_DL_THROUGHPUT"]]
                        else:
                            self.lastcdr.update(pdcpdrateRes)
                            self.pdcpD_AvgThp.append(pdcpdrateRes["PDCP_DL_THROUGHPUT"])

                    elif lb[0] == "PDCPRATEU":
                        pdcpurateRes = pdcprateu.parseline(lb)
                        if self.cdr["LON"] == None:
                            self.cdr.update(pdcpurateRes)
                            self.pdcpU_AvgThp = [pdcpurateRes["PDCP_UL_THROUGHPUT"]]
                        else:
                            self.lastcdr.update(pdcpurateRes)
                            self.pdcpU_AvgThp.append(pdcpurateRes["PDCP_UL_THROUGHPUT"])

                    elif lb[0] == "PLAID":
                        plaidRes = plaid.parseline(lb)
                        if plaidRes == {}: break #dont do anything is results are blank
                        if self.cdr["LON"] == None:
                            self.cdr.update(plaidRes)
                        else:
                            #print(lb, plaidRes)
                            self.lastcdr.update(plaidRes)

                    elif lb[0] == "PLAIU":
                        plaiuRes = plaiu.parseline(lb)
                        if plaiuRes == {}: break  # dont do anything is results are blank
                        if self.cdr["LON"] == None:
                            self.cdr.update(plaiuRes)
                        else:
                            #print(lb, plaiuRes)
                            self.lastcdr.update(plaiuRes)

                    ##########################################################

                    ##########################################################
                    #This should be the last line in this loop (while currline)
                    currline = f.readline().upper()
                    ##########################################################

            print("File processed. Returning the results as a dictionary now. ")
            #print(self.results)
            df = pd.DataFrame.from_records(self.results)
            fExpName =  os.path.join(os.path.split(self.filename)[0], "res_" + (str(datetime.now().time())).replace(":","_") + ".csv")
            print("File = ", self.filename,". Exported results in ", fExpName)
            df.to_csv(fExpName, index=False)

            return self.results
#            except Exception as e:
#                print("An exception ocurred while reading the file. ", e)

