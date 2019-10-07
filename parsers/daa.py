from parsers.const import *

F_DAAAPPPROT = "DAA_APP_PROTOCOL"
F_DAAHOSTADDRESS = "DAA_HOST_ADDRESS"
F_DAAHOSTPORT = "DAA_HOST_PORT"
F_DAACONNTIMEOUT = "DAA_CONNECT_TIMEOUT"
F_DAASECPROT = "DAA_SECURITY_PROTOCOL"
F_DAAAUTHSCHEME = "DAA_AUTH_SCHEME"

appProtocol = {0 : "NEMO protocol using MODEM",
               1 : "NEMO protocol using TCP",
               2: "NEMO protocol using UDP",
               3: "FTP",
               4: "HTPP",
               5: "SMTP",
               6: "POP3",
               7: 'MMS',
               8: 'WAP 1.0',
               9: 'Streaming (VLC or YouTube)',10 : 'WAP 2.0',
                11 : 'HTTP browsing',
                12 : 'ICMP ping',
                13 : 'IPerf over TCP',
                14 : 'IPerf over UDP',
                15 : 'Trace route',
                16 : 'SFTP',
                17 : 'IMAP',
                18 : 'Facebook',
                19 : 'Twitter',
                20 : 'Instagram',
                21 : 'LinkedIn',
                22 : 'Youtube PEVQ-S',
                23 : 'Dropbox',
                24 : 'Speedtest',
                25 : 'mScore',
                26 : 'Netflix',
                27 : 'WhatsApp'
               }

secProtocol = {0 : "None",
               1: "SSL",
               2: "SSH"}

authScheme = {0 : "Basic",
              1: "Digest",
              3: "None",
              4: "NTLM",
              5: "Negotiate"}


def parseline(pline):
    ret = {}
    ret[F_TIME] = pline[1]
    ret[F_EVENT] = "DAA"
    ret[F_EVENTNAME] = "Data Connection Attempt"
    pline = pline[2:]

    currKey = ret[F_EVENT]

    try:
        ret[currKey + "_" + F_NUMCONTEXT] = int(pline[0])
        ret[currKey + "_" + F_CONTEXTS] = "_".join([pline[x] for x in range(1, 1 + ret[currKey + "_" + F_NUMCONTEXT])])
    except Exception as e:
        ret[currKey + "_" + F_NUMCONTEXT] = 0
        ret[currKey + "_" + F_CONTEXTS] = ""
    pline = pline[1 + ret[currKey + "_" + F_NUMCONTEXT] : ] #remove pline with all context ids

    try:
        ret[F_DAAAPPPROT] = appProtocol[int(pline[0])]
    except:
        ret[F_DAAAPPPROT] = "UNK"

    ret[F_DAAHOSTADDRESS] = pline[1]
    ret[F_DAAHOSTPORT] = pline[2]
    try:
        ret[F_DAACONNTIMEOUT] = int(pline[3])
    except:
        ret[F_DAACONNTIMEOUT] = np.nan

    try:
        ret[F_DAASECPROT] = secProtocol[int(pline[4])]
    except:
        ret[F_DAASECPROT] = "UNK"

    try:
        ret[F_DAAAUTHSCHEME] = authScheme[int(pline[5])]
    except:
        ret[F_DAAAUTHSCHEME] = "UNK"

    return ret