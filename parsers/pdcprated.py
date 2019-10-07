from parsers.const import *

F_PDCPRATEDMEASSYS = "PDCPDRATE_MEAS_SYSTEM"

measSys = { 7 : 'LTE FDD (or NB-IOT)' ,
            8 : 'LTE TDD'
}

def parseline(pline, fileformat=234):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "PDCPRATED"
    ret[F_EVENTNAME] = "PDCP DL MEASUREMENTS"
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
        ret[F_PDCPRATEDMEASSYS] = measSys[measSysInt]
    except:
        ret[F_PDCPRATEDMEASSYS] = "UNK"
        return

    pline = pline[1:]

    try:
        hC = int(pline[0])
        assert hC == 2 #as per v2.34
        pdcpHeader = ["PDCP_DL_THROUGHPUT", "PDCP_DL_BLOCKS"]
        pdcpTypes = [int, int]

        pdcpRBHeader = ["PDCP_DL_RB_ID", "PDCP_DL_THROUGHPUT_ON_RB", "PDCP_DL_BLOCKS_ON_RB"]
        pdcpRBTypes = [int, int, int]

        pdcpHeader = pdcpHeader[:hC]

        pline = pline[1:]

        hCItems = pline[0: hC]
        hCItems = [convTypes(hCItems[x], pdcpTypes[x]) for x in range(0, len(hCItems))]
        ret.update(dict(zip([x for x in pdcpHeader], hCItems)))

        pline = pline[hC:]

        numRBs = int(pline[0])
        paramsPerRB = int(pline[1])

        pline = pline[2:]
        for i in range(numRBs):
            hCItems = pline[0: paramsPerRB]
            hCItems = [convTypes(hCItems[x], pdcpRBTypes[x]) for x in range(0, len(hCItems))]
            ret.update(dict(zip([x + "_" + str(i) for x in pdcpRBHeader], hCItems)))
            pline = pline[paramsPerRB:]

    except Exception as e:
        print("An exception occurred decoding pdcp dl. ", e)
        return {}

    return ret
