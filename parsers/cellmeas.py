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
    ret[F_EVENT] = "CMDREQ"
    ret[F_EVENTNAME] = "Command Request"
    pline = pline[2:]

    try:
        ret[F_NUMCONTEXT] = int(pline[0])
        ret[F_CONTEXTS] = "_".join([pline[x] for x in range(1, 1 + ret[F_NUMCONTEXT])])
    except Exception as e:
        ret[F_NUMCONTEXT] = 0
        ret[F_CONTEXTS] = ""
    pline = pline[1 + ret[F_NUMCONTEXT] : ] #remove pline with all context ids


    measSysInt = -1
    try:
        measSysInt = int(pline[0])
        ret[F_CELLMEASSYS] = measSys[measSysInt]
    except:
        ret[F_CELLMEASSYS] = "UNK"
        return

    pline = pline[1:]

    if measSysInt == 1:

        try:
            hC = int(pline[0])
            assert hC == 0 #as there were no header parameters defined in File format v2.34 NEMO.
            numCells = int(pline[1])
            paramsPerCell = int(pline[2])

            if paramsPerCell == 15:
                gsmHeader = ["CELL_TYPE", "BAND", "ARFCN_UARFCN_EARFCN_NRARFCN", "BSIC_PSC_PCI", "RXLEV_FULL_RSSI",
                             "RXLEV_SUB_RSRP",
                             "GSM_C1", "GSM_C2", "GSM_C31", "GSM_C32", "HCS_PRIORITY", "HCS_THRESHOLD", "CELLID",
                             "LAC_TAC",
                             "RAC"]
            elif paramsPerCell == 16:
                gsmHeader = ["CELL_TYPE", "BAND", "ARFCN_UARFCN_EARFCN_NRARFCN", "BSIC_PSC_PCI", "RXLEV_FULL_RSSI",
                             "RXLEV_SUB_RSRP",
                             "GSM_C1", "GSM_C2", "GSM_C31", "GSM_C32", "HCS_PRIORITY", "HCS_THRESHOLD", "CELLID",
                             "LAC_TAC",
                             "RAC", "SRXLEV"]
            else:
                assert True == False #we dont know this header length parameters
                return

            pline = pline[3:]

            assert paramsPerCell == len(gsmHeader)

            for i in range(numCells):
                hCItems = pline[0: paramsPerCell]
                ret.update(dict(zip([x + "_" + str(i) for x in gsmHeader], hCItems)))
                ret.update(dict(zip(gsmHeader, hCItems)))
                pline = pline[paramsPerCell:]  # discard earlier parameters already processed. Eases future calculations

        except Exception as e:
            print("Exception in loop for gsm header check", e)
            return

    elif measSysInt == 7: #LTE-FDD or NB-IOT
        if fileformat == 227:
            lteHeader = ["CELL_TYPE", "BAND",  "ARFCN_UARFCN_EARFCN_NRARFCN", "BSIC_PSC_PCI", "RXLEV_FULL_RSSI", "RXLEV_SUB_RSRP",
                         "RSRQ", "TIMING", "PATHLOSS"]
        elif fileformat > 227:
            lteHeader = ["CELL_TYPE", "BAND", "ARFCN_UARFCN_EARFCN_NRARFCN", "BSIC_PSC_PCI", "RXLEV_FULL_RSSI",
                         "RXLEV_SUB_RSRP",
                         "RSRQ", "TIMING", "PATHLOSS", "SRXLEV"]
        else:
            lteHeader = ["CELL_TYPE", "BAND", "ARFCN_UARFCN_EARFCN_NRARFCN", "BSIC_PSC_PCI", "RXLEV_FULL_RSSI",
                         "RXLEV_SUB_RSRP",
                         "RSRQ", "TIMING", "PATHLOSS", "SRXLEV"]
        try:
            hC = int(pline[0])
            assert hC == 0 #as v2.34 has no Header parameters
            numCells = int(pline[1])
            paramsPerCell = int(pline[2])

            pline = pline[3:]

            assert paramsPerCell == len(lteHeader)

            detCount = 0
            listCount = 0

            for i in range(numCells):
                hCItems = pline[0: paramsPerCell]
                cT = int(pline[0])
                if cT == 0:
                    preF = "SERV_"
                    ret.update(dict(zip([preF + x for x in lteHeader], hCItems)))
                elif cT == 1:
                    preF = "LISTED_"
                    listCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(listCount) for x in lteHeader], hCItems)))
                elif cT == 2:
                    preF = "DETECTED_"
                    detCount += 1
                    ret.update(dict(zip([preF + x + "_" + str(detCount) for x in lteHeader], hCItems)))
                elif cT == 10:
                    preF = "SCELL1_"
                    ret.update(dict(zip([preF + x for x in lteHeader], hCItems)))
                elif cT == 11:
                    preF = "SCELL2_"
                    ret.update(dict(zip([preF + x for x in lteHeader], hCItems)))
                elif cT == 12:
                    preF = "SCELL3_"
                    ret.update(dict(zip([preF + x for x in lteHeader], hCItems)))
                elif cT == 13:
                    preF = "SCELL4_"
                    ret.update(dict(zip([preF + x for x in lteHeader], hCItems)))
                else:
                    preF = "UNK_"
                    ret.update(dict(zip([preF + x + "_" + str(i) for x in lteHeader], hCItems)))

                pline = pline[paramsPerCell:]
        except Exception as e:
            print("Exception in loop for LTE header check", e)
            return
    #print(ret)
    return ret