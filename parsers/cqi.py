from parsers.const import *

F_CQISYSTEM = "CQI_MEAS_SYSTEM"
F_CQIHEADERS = ["U_CQI", "U_CQI_2", "L_WB_CQI0", "L_WB_CQI1", "L_SB_CQI0", "L_SB_CQI1"]

measSys = { 5 : 'UMTS FDD' ,
            6 : 'UMTS TD-SCDMA',
            7 : 'LTE FDD (or NB-IOT)' ,
            8 : 'LTE TDD'
}

def parseline(pline, fileformat=234):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "CQI"
    ret[F_EVENTNAME] = "CHANNEL QUALITY MEASUREMENTS"
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
        ret[F_CQISYSTEM] = measSys[measSysInt]
    except:
        ret[F_CQISYSTEM] = "UNK"
        return

    pline = pline[1:]

    if measSysInt == 5:
        try:
            umtsHeader = ["U_CQISAMPLE_DURATION", "U_CQI_REQUESTED_THROUGHPUT", "U_CQI_REPETITIONS", "U_CQI_FEEDBACK_CYCLE",
                             "U_MIMO_RANK2_RATIO"]
            umtsTypes= [int, int, int, int,
                        float]

            cqiHeader = ["U_CQI_PERCENTAGE", "U_CQI", "U_CQI_TYPE", "U_CQI_2", "U_CQI_CELLTYPE"]
            cqiTypes = [float, int, int, int, int]

            hC = int(pline[0])
            assert hC == 5 #v2.34

            pline = pline[1:]

            hCItems = pline[: hC]
            hCItems = [convTypes(hCItems[x], umtsTypes[x]) for x in range(0, len(hCItems))]
            ret.update(dict(zip([x for x in umtsHeader], hCItems)))
            pline = pline[hC:]

            numCQIs = int(pline[0])
            paramsPerCQI = int(pline[1])

            pline = pline[2:]

            primCount = 0
            secCount = 0
            for i in range(numCQIs):
                cT = pline[4]  # this should be the cell Type
                hCItems = pline[0: paramsPerCQI]
                hCItems = [convTypes(hCItems[x], cqiTypes[x]) for x in range(0, len(hCItems))]
                if cT == 1:
                    preF = "PRIMARY"
                    primCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(primCount) for x in cqiHeader], hCItems)))
                elif cT == 2:
                    preF = "SECONDARY"
                    secCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(secCount) for x in cqiHeader], hCItems)))
                else:
                    preF = "UNK"
                    ret.update(dict(zip([preF + x + "_" + str(i) for x in cqiHeader], hCItems)))
                pline = pline[paramsPerCQI: ]
        except Exception as e:
            print("An exception occurred for CQI UMTS FDD", e)
            return {}

    elif measSysInt == 6:
        try:
            umtsHeader = ["U_CQISAMPLE_DURATION", "U_CQI_REQUESTED_THROUGHPUT"]
            umtsTypes= [int, int]

            cqiHeader = ["U_CQI_PERCENTAGE", "U_CQI"]
            cqiTypes = [float, int]

            hC = int(pline[0])
            assert hC == 2 #v2.34

            pline = pline[1:]

            hCItems = pline[: hC]
            hCItems = [convTypes(hCItems[x], umtsTypes[x]) for x in range(0, len(hCItems))]
            ret.update(dict(zip([x for x in umtsHeader], hCItems)))
            pline = pline[hC:]

            numCQIs = int(pline[0])
            paramsPerCQI = int(pline[1])

            pline = pline[2:]

            for i in range(numCQIs):
                hCItems = pline[0: paramsPerCQI]
                hCItems = [convTypes(hCItems[x], cqiTypes[x]) for x in range(0, len(hCItems))]
                ret.update(dict(zip([x for x in cqiHeader], hCItems)))
                pline = pline[paramsPerCQI: ]

        except Exception as e:
            print("An exception occurred for CQI UMTS TD-SCDMA", e)
            return {}

    elif (measSysInt == 7) or (measSysInt == 8):
        try:
            lteHeader = ["L_CQI_SAMPDURATION", "L_CQI_REQUESTED_THROUGHPUT", "L_WB_CQI0", "L_WB_CQI1",
                         "L_SB_CQI0", "L_SB_CQI1", "L_WB_PMI", "L_CQI_CELL_TYPE"]
            lteTypes = [int, int, int, int,
                        int, int, int, int]

            lteRankHeader = ["L_CQI_REQUESTED_RANK", "L_CQI_RANK"]
            lteRankTypes = [float, int]

            lteCqiSubBandHeader = ["L_CQI_SB_INDEX", "L_CQI0_FOR_SUBBAND", "L_CQI1_FOR_SUBBAND"]
            lteCqiSubBandTypes = [int, int, int]


            hC = int(pline[0])
            assert hC == 8 #v2.34

            pline = pline[1:]

            hCItems = pline[: hC]
            hCItems = [convTypes(hCItems[x], lteTypes[x]) for x in range(0, len(hCItems))]
            ret.update(dict(zip([x for x in lteHeader], hCItems)))
            pline = pline[hC:]

            numRanks = int(pline[0])
            paramsPerRanks = int(pline[1])

            pline = pline[2:]

            for i in range(numRanks):
                hCItems = pline[0: paramsPerRanks]
                hCItems = [convTypes(hCItems[x], lteRankTypes[x]) for x in range(0, len(hCItems))]
                ret.update(dict(zip([x for x in lteRankHeader], hCItems)))
                pline = pline[paramsPerRanks: ]

            numCQISB = int(pline[0])
            paramsPerCQISB = int(pline[1])

            pline = pline[2:]

            for i in range(numCQISB):
                hCItems = pline[0: paramsPerCQISB]
                hCItems = [convTypes(hCItems[x], lteCqiSubBandTypes[x]) for x in range(0, len(hCItems))]
                ret.update(dict(zip([x for x in lteCqiSubBandHeader], hCItems)))
                pline = pline[paramsPerCQISB: ]

        except Exception as e:
            print("An exception occurred for CQI LTE", e)
            return {}

    else:
        print("Option not implemented")
        assert False

    return ret

