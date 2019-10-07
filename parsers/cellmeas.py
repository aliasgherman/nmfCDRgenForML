from parsers.const import *

F_CELLMEASSYS = "CELLMEAS_MEAS_SYSTEM"

measSys = {1 : 'GSM' ,
            2 : 'TETRA' ,
            5 : 'UMTS FDD' ,
            6 : 'UMTS TD-SCDMA' ,
            7 : 'LTE FDD (or NB-IOT)' ,
            8 : 'LTE TDD' ,
            10 : 'cdmaOne' ,
            11 : 'CDMA 1x' ,
            12 : 'EVDO' ,
            20 : 'WLAN' ,
            21 : 'GAN WLAN' ,
            25 : 'WiMAX' ,
            51 : 'AMPS' ,
            52 : 'NAMPS' ,
            53 : 'DAMPS' ,
            55 : 'iDEN' ,
}

def parseline(pline, fileformat=234):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "CELLMEAS"
    ret[F_EVENTNAME] = "CELL MEASUREMENTS"
    pline = pline[2:]

    currKey = ret[F_EVENT]

    try:
        ret[currKey + "_" + F_NUMCONTEXT] = int(pline[0])
        ret[currKey + "_" + F_CONTEXTS] = "_".join([pline[x] for x in range(1, 1 + ret[currKey + "_" + F_NUMCONTEXT])])
    except Exception as e:
        ret[currKey + "_" + F_NUMCONTEXT] = 0
        ret[currKey + "_" + F_CONTEXTS] = ""
    pline = pline[1 + ret[currKey + "_" + F_NUMCONTEXT] : ] #remove pline with all context ids


    #measSysInt = -1 current code branching does not need initial assignment here.
    try:
        measSysInt = int(pline[0])
        ret[F_CELLMEASSYS] = measSys[measSysInt]
    except:
        ret[F_CELLMEASSYS] = "UNK"
        return

    pline = pline[1:]

    if measSysInt == 1:

        try:
            gsmHeader = ["G_CELL_TYPE", "G_BAND", "G_ARFCN", "G_BSIC", "G_RXLEV_FULL",
                             "G_RXLEV_SUB",
                             "GSM_C1", "GSM_C2", "GSM_C31", "GSM_C32", "G_HCS_PRIORITY", "G_HCS_THRESHOLD", "G_CELLID",
                             "G_LAC",
                             "G_RAC", "G_SRXLEV"]
            gsmTypes = [int, int, int, int, float,
                        float,
                        float, float, float, float, int, float, int,
                        int,
                        int, float]
            hC = int(pline[0])
            assert hC == 0 #as there were no header parameters defined in File format v2.34 NEMO.

            r, pline = processSets(pline=pline, idxNumSets=1, idxParamsPerSet=2, setTypes=gsmTypes, setHeader=gsmHeader,
                        idxCustomDictPara=0, customPrefDict=None)
            ret.update(r)

            # numCells = int(pline[1])
            # paramsPerCell = int(pline[2])
            #
            # gsmHeader = gsmHeader[:paramsPerCell] #trim gsmheader as older formats may have less fields
            #
            # pline = pline[3:]
            #
            # #assert paramsPerCell == len(gsmHeader)
            #
            # for i in range(numCells):
            #     hCItems = pline[0: paramsPerCell]
            #     hCItems = [convTypes(hCItems[x], gsmTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([x + "_" + str(i) for x in gsmHeader[:paramsPerCell]], hCItems)))
            #     #ret.update(dict(zip(gsmHeader, hCItems)))
            #     pline = pline[paramsPerCell:]  # discard earlier parameters already processed. Eases future calculations

        except Exception as e:
            print("Exception in loop for gsm header check", e)
            return

    elif measSysInt == 7: #LTE-FDD or NB-IOT
        lteHeader = ["L_CELL_TYPE", "L_BAND", "L_EARFCN", "L_PCI", "L_RSSI",
                         "L_RSRP",
                         "L_RSRQ", "L_TIMING", "L_PATHLOSS", "L_SRXLEV"]
        lteTypes = [int, int, int, int, float,
                    float,
                    float, int, float, float]
        try:
            hC = int(pline[0])
            assert hC == 0 #as v2.34 has no Header parameters

            r, pline = processSets(pline=pline, setTypes=lteTypes, setHeader=lteHeader, customPrefDict={'0': "SERV", '1' : "LISTED",
                                                                        '2' : 'DETECTED', '10' : 'SCELL1',
                                                         '11' : 'SCELL2', '12' : 'SCELL3', '13' : 'SCELL4'},
                        idxCustomDictPara=0,idxNumSets=1, idxParamsPerSet=2)
            ret.update(r)

        except Exception as e:
            print("Exception in loop for LTE header check", e)
            return
    elif measSysInt == 5: #UMTS-FDD
        umtsHeader_Cell = ["U_CELL_TYPE", "U_BAND", "U_UARFCN", "U_PSC", "U_ECN0", "U_STTD",
                         "U_RSCP",
                         "U_SECONDARY_SC", "U_SQUAL", "U_SRXLEV", "U_HQUAL", "U_HRXLEV", "U_RQUAL", "U_RRXLEV", "U_OFF", "U_TM", "U_PATHLOSS"]
        umtsCellTypes = [int, int, int, int, float, int,
                         float,
                         int, float, float, float, float, float, float, int, float, float]

        umtsHeader_Chan = ["U_CHANNEL_NUM", "U_CHANNEL_RSSI", "U_CHANNEL_BAND"]
        umtsChanTypes = [int, float, int]
        try:
            hC = int(pline[0])
            assert hC == 0 #headers have no parameters in v2.34

            r, pline = processSets(pline=pline, setTypes=umtsChanTypes, setHeader=umtsHeader_Chan, customPrefDict=None,
                                   idxCustomDictPara=0, idxNumSets=1, idxParamsPerSet=2)
            ret.update(r)

            # numChans = int(pline[1])
            # paramsPerChan = int(pline[2])
            # umtsHeader_Chan = umtsHeader_Chan[:paramsPerChan] #trim header as old files may have less elements
            # pline = pline[3:]
            #
            # for i in range(numChans):
            #     hCItems = pline[0: paramsPerChan]
            #     hCItems = [convTypes(hCItems[x], umtsChanTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([x + "_" + str(i)for x in umtsHeader_Chan], hCItems)))
            #     pline = pline[paramsPerChan:]

            #hC = int(pline[0])
            #assert hC == 0 #No header parameters defined for v2.34

            r, pline = processSets(pline=pline, setTypes=umtsCellTypes, setHeader=umtsHeader_Cell,
                                   customPrefDict={'0' : "ACTIVE", '1' : "MONITORED", '2' : "DETECTED", '3' : 'UNDETECTED'},
                                   idxCustomDictPara=0, idxNumSets=0, idxParamsPerSet=1)
            ret.update(r)

            # numCells = int(pline[0])
            # paramsPerCell = int(pline[1])
            #
            # umtsHeader_Cell = umtsHeader_Cell[:paramsPerCell]
            #
            # pline = pline[2:]
            #
            # monCount = 0
            # detCount = 0
            # actCount = 0
            # undetCount = 0
            #
            # for i in range(numCells):
            #     hCItems = pline[0: paramsPerCell]
            #     hCItems = [convTypes(hCItems[x], umtsCellTypes[x]) for x in range(0, len(hCItems))]
            #     cT = int(pline[0])
            #     if cT == 0:
            #         preF = "ACTIVE"
            #         actCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(actCount) for x in umtsHeader_Cell], hCItems)))
            #     elif cT == 1:
            #         preF = "MONITORED"
            #         monCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(monCount) for x in umtsHeader_Cell], hCItems)))
            #     elif cT == 2:
            #         preF = "DETECTED"
            #         detCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(detCount) for x in umtsHeader_Cell], hCItems)))
            #     elif cT == 3:
            #         preF = "UNDETECTED"
            #         undetCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(undetCount) for x in umtsHeader_Cell], hCItems)))
            #     else:
            #         preF = "UNK"
            #         ret.update(dict(zip([preF + x + "_" + str(i) for x in umtsHeader_Cell], hCItems)))
            #     pline = pline[paramsPerCell:]
        except Exception as e:
            print("Exception in loop for UMTS FDD header check", e)
            return

    elif measSysInt == 6: #UMTS TD-SCDMA
        umtsHeader_Cell = ["U_CELL_TYPE", "U_BAND", "U_UARFCN", "U_CELLPARAMS_ID", "U_RSCP",
                         "U_SRXLEV", "U_HRXLEV", "U_RRXLEV", "U_PATHLOSS"]
        umtsCellTypes = [int, int, int, int, float,
                         float, float, float, float]

        umtsHeader_Chan = ["U_CHANNEL_BAND", "U_CHANNEL_NUM", "U_CHANNEL_RSSI"]
        umtsChanTypes = [int, int, float]
        try:
            hC = int(pline[0])
            assert hC == 0 #headers have no parameters in v2.34

            r, pline = processSets(pline=pline, setHeader=umtsHeader_Chan, setTypes=umtsChanTypes, customPrefDict=None,
                        idxCustomDictPara=0, idxNumSets=1, idxParamsPerSet=2)

            ret.update(r)
            # numChans = int(pline[1])
            # paramsPerChan = int(pline[2])
            # umtsHeader_Chan = umtsHeader_Chan[:paramsPerChan] #trim header as old files may have less elements
            # pline = pline[3:]
            #
            # for i in range(numChans):
            #     hCItems = pline[0: paramsPerChan]
            #     hCItems = [convTypes(hCItems[x], umtsChanTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([x + "_" + str(i)for x in umtsHeader_Chan], hCItems)))
            #     pline = pline[paramsPerChan:]

            #hC = int(pline[0])
            #assert hC == 0 #No header parameters defined for v2.34

            r, pline = processSets(pline=pline, setTypes=umtsCellTypes, setHeader=umtsHeader_Cell,
                        customPrefDict={'0' : 'NEIGHBOR', '1' : 'SERVING'}, idxCustomDictPara=0,
                        idxNumSets=0, idxParamsPerSet=1)

            ret.update(r)

            # numCells = int(pline[0])
            # paramsPerCell = int(pline[1])
            #
            # umtsHeader_Cell = umtsHeader_Cell[:paramsPerCell]
            #
            # pline = pline[2:]
            #
            # nCount = 0
            # sCount = 0
            #
            # for i in range(numCells):
            #     hCItems = pline[0: paramsPerCell]
            #     hCItems = [convTypes(hCItems[x], umtsCellTypes[x]) for x in range(0, len(hCItems))]
            #     cT = int(pline[0])
            #     if cT == 0:
            #         preF = "NEIGHBOR"
            #         nCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(nCount ) for x in umtsHeader_Cell], hCItems)))
            #     elif cT == 1:
            #         preF = "SERVING"
            #         sCount += 1
            #         ret.update(dict(zip([preF + x + "_" + str(sCount) for x in umtsHeader_Cell], hCItems)))
            #     else:
            #         preF = "UNK"
            #         ret.update(dict(zip([preF + x + "_" + str(i) for x in umtsHeader_Cell], hCItems)))
            #     pline = pline[paramsPerCell:]
        except Exception as e:
            print("Exception in loop for UMTS FDD header check", e)
            return

    else:
        print("This option is unimplemented. CELLMEAS, systemtype = ", measSysInt)
        assert False


        #print(ret)
    return ret