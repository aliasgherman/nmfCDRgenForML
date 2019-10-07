from parsers.const import *

F_PLAIUMEASSYS = "PLAIU_MEAS_SYSTEM"

measSys = { 5 : 'UMTS FDD' ,
            6 : 'UMTS TD-SCDMA' ,
            7 : 'LTE FDD (or NB-IOT)' ,
            8 : 'LTE TDD',
            25 : 'WiMAX'
}

def parseline(pline, fileformat=234):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "PLAIU"
    ret[F_EVENTNAME] = "UPLINK LINK ADAPTATION"
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
        ret[F_PLAIUMEASSYS] = measSys[measSysInt]
    except:
        ret[F_PLAIUMEASSYS] = "UNK"
        return

    pline = pline[1:]

    if (measSysInt == 7) or (measSysInt == 8): #LTE

        try:
            lteHeader = ["PLAIU_SAMP_DUR", "UL_PRB_UTIL", "UL_TBS", "MAX_UL_TBS", "PLAIU_CELL_TYPE"]
            lteTypes = [int, float, int, int, int]

            plaHeader = ["PUSCH_MODULATION_PERCENT", "PLAIU_PUSCH_RANK", "PLAIU_PUSCH_CW0_MODULATION",
                         "PLAIU_PUSCH_CW0_MCS", "PLAIU_PUSCH_CW1_MODULATION",
                         "PLAIU_PUSCH_CW1_MCS", "PLAIU_PUSCH_REPETITIONS", "PLAIU_PUSCH_CW0_TBS",
                         "PLAIU_PUSCH_CW1_TBS"]
            plaTypes = [float, int, int,
                        int, int,
                        int, int, int,
                        int]

            prbHeader = ["PLAIU_PUSCH_PRB_PERCENT", "PLAIU_PUSCH_PRB_NUM", "PLAIU_PUSCH_SUBFRAMES_NBIOT"]
            prbTypes = [float, int, int]

            prbIndexHeader = ["PLAIU_UL_PRB_UTIL_FOR_INDEX", "PLAIU_UL_PRB_UTIL_INDEX_NUM"]
            prbIndexTypes = [float, int]

            hC = int(pline[0])
            assert hC == 5 #as there were no header parameters defined in File format v2.34 NEMO.
            pline = pline[1:]

            r, pline = processSets(pline=pline, setTypes=lteTypes, setHeader=lteHeader, customPrefDict={'0': "PCELL", '1': "SCELL1", '2': "SCELL2", '3': "SCELL3", '4': "SCELL4"}
                                   , idxCustomDictPara=4
                        ,idxNumSets=None, idxParamsPerSet=hC)
            ret.update(r)

            # cT = int(pline[4])
            # cTDict = {0: "PCELL", 1: "SCELL1", 2: "SCELL2", 3: "SCELL3", 4: "SCELL4"}
            # preF = cTDict[cT]
            # lteHeader = lteHeader[:hC]
            #
            # hCItems = pline[:hC]
            # hCItems = [convTypes(hCItems[x], lteTypes[x]) for x in range(0, len(hCItems))]
            # ret.update(dict(zip([preF + "_" + x for x in lteHeader[:hC]], hCItems)))
            # pline = pline[hC:]

            r, pline = processSets(pline=pline, setTypes=plaTypes, setHeader=plaHeader, customPrefDict=None, idxCustomDictPara=0,
                        idxNumSets=0, idxParamsPerSet=1)
            ret.update(r)
            # numPLASets = int(pline[0])
            # paramsPerPLA = int(pline[1])
            #
            # plaHeader = plaHeader[:paramsPerPLA]
            #
            # pline = pline[2:]
            #
            # for i in range(numPLASets):
            #     hCItems = pline[0: paramsPerPLA]
            #     hCItems = [convTypes(hCItems[x], plaTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([preF + "_" + x + "_"  + str(i) for x in plaHeader], hCItems)))
            #     pline = pline[paramsPerPLA:]

            r, pline = processSets(pline=pline, setTypes=prbTypes, setHeader=prbHeader, customPrefDict=None, idxCustomDictPara=0,
                                   idxNumSets=0, idxParamsPerSet=1)
            ret.update(r)

            # numPRBs = int(pline[0])
            # paramsPerPRB = int(pline[1])
            # prbHeader = prbHeader[:paramsPerPRB]
            #
            # pline = pline[2:]
            #
            # for i in range(numPRBs):
            #     hCItems = pline[0: paramsPerPRB]
            #     hCItems = [convTypes(hCItems[x], prbTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([preF + "_" + x + "_"  + str(i) for x in prbHeader], hCItems)))
            #     pline = pline[paramsPerPRB:]

            r, pline = processSets(pline=pline, setTypes=prbIndexTypes, setHeader=prbIndexHeader, customPrefDict=None,
                                   idxCustomDictPara=0, idxNumSets=0, idxParamsPerSet=1)
            ret.update(r)

            # numPRBIndex = int(pline[0])
            # paramsPerPRBIndex = int(pline[1])
            # prbIndexHeader = prbIndexHeader[:paramsPerPRBIndex]
            #
            # pline = pline[2:]
            #
            # for i in range(numPRBIndex):
            #     hCItems = pline[0: paramsPerPRBIndex]
            #     hCItems = [convTypes(hCItems[x], prbIndexTypes[x]) for x in range(0, len(hCItems))]
            #     ret.update(dict(zip([preF + "_" + x + "_"  + str(i) for x in prbIndexHeader], hCItems)))
            #     pline = pline[paramsPerPRBIndex:]

        except Exception as e:
            print("Exception in loop for PLAIU check", e)
            return

    else:
        print("Option not implemented")
        assert False

    return ret
