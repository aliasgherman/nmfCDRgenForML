from parsers.const import *

F_GPSLON = "LONGITUDE"
F_GPSLAT = "LATITUDE"
F_GPSHEIGHT = "HEIGHT"
F_GPSDISTANCE = "DISTANCE"
F_GPSQUAL = "GPS_QUALITY"
F_GPSSATELLITE = "GPS_SATELLITES"
F_GPSVELOCITY = "GPS_VELOCITY"
F_GPSPDOP = "GPS_POS_DILUTION_OF_PRECISION"
F_GPSHDOP = "GPS_HORIZONTAL_DILUTION_OF_PRECISION"
F_GPSVDOP = "GPS_VERTICAL_DILUTION_OF_PRECISION"
F_GPSSTATUS = "GPS_STATUS"

gpsQual = {-1 : 'Simulated GPS fix',
            0 : 'No fix',
            1 : 'GPS fix',
            2 : 'GGPS fix',
            3 : 'DR in use',
            4 : 'GPS estimation',
            5 : 'GPS fix with DR',
            6 : 'DGPS fix with DR',
            11 : 'Glonass fix',
            21 : 'GPS + Glonass fix',
}

gpsStatus = { 0 : 'No fix',
1 : 'Fix Normal State',
2 : 'GPS Time drift detected',
3 : 'Stale position'
}

def parseline(pline, fileformat=227):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "GPS"
    ret[F_EVENTNAME] = "GPS Position"
    pline = pline[2:]
    #print(pline[0], int(pline[0]))

    try:
        ret[F_NUMCONTEXT] = int(pline[0])
        ret[F_CONTEXTS] = "_".join([pline[x] for x in range(1, 1 + ret[F_NUMCONTEXT])])
    except Exception as e:
        ret[F_NUMCONTEXT] = 0
        ret[F_CONTEXTS] = ""
    pline = pline[1 + ret[F_NUMCONTEXT] : ] #remove pline with all context ids

    ret[F_GPSLON] = pline[0]
    ret[F_GPSLAT] = pline[1]
    ret[F_GPSHEIGHT] = pline[2]
    ret[F_GPSDISTANCE] = pline[3]

    try:
        ret[F_GPSQUAL] = gpsQual[int(pline[4])]
    except:
        ret[F_GPSQUAL] = "UNK"

    ret[F_GPSSATELLITE] = pline[5]
    ret[F_GPSVELOCITY] = pline[6]
    ret[F_GPSPDOP] = pline[7]
    ret[F_GPSHDOP] = pline[8]
    ret[F_GPSVDOP] = pline[9]

    try:
        ret[F_GPSSTATUS] = gpsStatus[int(pline[10])]
    except:
        ret[F_GPSSTATUS] = "UNK"

    return ret