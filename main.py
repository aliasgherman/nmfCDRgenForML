import os
import pandas as pd
import io
from statsgen.StatsGenerator import StatsGenerator
from cdrgen.cdrgen import CDRGenerator
from parsers import parserEvents, daa, gps
import time

from infostruct.infostruct import InfoStruct


testdir = "/home/aamhabiby/Desktop/scriptTest/htp test new apk/f8vsZF5M-C5h_nmf/"
NEWLINE = "\n"

parserObjs = {"#" : parserEvents, "DAA" : daa, "GPS" :  gps}

def main():
    print("Inside the main function.")
    files = getFiles(testdir, ".nmf")
    for file in files:
        st_time = time.time()
        print("Processing file ", file)
        #sg = StatsGenerator(filename=file, NEWLINE=NEWLINE)
        #res = sg.run()
        cg = CDRGenerator(filename=file, NEWLINE=NEWLINE)
        res = cg.run()
        readfile(file)
        #df.to_csv(os.path.join(testdir, "testfile.csv"), index=False)
        print("Total time taken ", time.time() - st_time)

def getFiles(directory, filter):
    files = [os.path.join(directory, x) for x in os.listdir(directory) if ((os.path.isfile(os.path.join(directory, x)) == True) and (x.find(filter) > -1))]
    return files

def readfile(filename):
    #df = pd.DataFrame()
    if os.path.isfile(filename):
        try:
            with io.open(filename, "r", newline=NEWLINE) as f:
                currline = f.readline().upper()
                while currline and currline.strip() != "":
                    currDict = {}
                    lb = currline.split(",")
                    if lb[0] in parserObjs.keys():
                        currDict = parserObjs[lb[0]].parseline(lb)
                        #df = pd.concat([df, pd.DataFrame.from_records([currDict])], axis = 0, ignore_index=True, sort=False) #concatenate dataframe rows

                    currline = f.readline().upper()
        except Exception as e:
            print("An exception ocurred while reading the file. ", e)
    #return df



if __name__ ==  "__main__":
    main()