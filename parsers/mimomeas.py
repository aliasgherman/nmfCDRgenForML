from parsers.const import *

F_MIMOMEASSYS = "MIMOMEAS_MEAS_SYSTEM"

measSys = { 5 : 'UMTS FDD' ,
            7 : 'LTE FDD (or NB-IOT)' ,
            8 : 'LTE TDD'
}

def parseline(pline, fileformat=234):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "MIMOMEAS"
    ret[F_EVENTNAME] = "MIMO MEASUREMENTS"
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
        ret[F_MIMOMEASSYS] = measSys[measSysInt]
    except:
        ret[F_MIMOMEASSYS] = "UNK"
        return

    pline = pline[1:]

    if measSysInt == 5:
        try:
            umtsHeader = ["U_BAND", "U_ARFCN", "U_PSC", "U_ANTENNA_PORT",
                             "U_CELLTYPE",
                             "U_MIMO_RSSI", "U_MIMOECN0", "U_MIMORSCP"]
            umtsTypes= [int, int, int, int,
                        int,
                        float, float, float]

            hC = int(pline[0])
            assert hC == 0 #as there were no header parameters defined in File format v2.34 NEMO.
            numMeas = int(pline[1])
            paramsPerMeas = int(pline[2])

            umtsHeader = umtsHeader[:paramsPerMeas] #trim gsmheader as older formats may have less fields

            pline = pline[3:]



            actCount = 0
            monCount = 0
            detCount = 0
            undetCount = 0

            for i in range(numMeas):
                cT = pline[4]  # this should be the cell Type
                hCItems = pline[0: paramsPerMeas]
                hCItems = [convTypes(hCItems[x], umtsTypes[x]) for x in range(0, len(hCItems))]
                if cT == 0:
                    preF = "ACTIVE"
                    actCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(actCount) for x in umtsHeader], hCItems)))
                elif cT == 1:
                    preF = "MONITORED"
                    monCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(monCount) for x in umtsHeader], hCItems)))
                elif cT == 2:
                    preF = "DETECTED"
                    detCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(detCount) for x in umtsHeader], hCItems)))
                elif cT == 3:
                    preF = "UNDETECTED"
                    undetCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(undetCount) for x in umtsHeader], hCItems)))
                else:
                    preF = "UNK"
                    ret.update(dict(zip([preF + x + "_" + str(i) for x in umtsHeader], hCItems)))
                pline = pline[paramsPerMeas:]
        except Exception as e:
            print("Exception occurred in MIMO Measurements. ", e)
            return {}
    else:
        print("This option is not implemented in MIMOMEAS. measSys = ", measSysInt)
        assert False


    return ret

            #assert paramsPerCell == len(gsmHeader)


