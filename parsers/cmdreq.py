from parsers.const import *

F_CMDREQINDEX = "CMDREQ_COMMAND_INDEX"
F_CMDREQCMDNAME = "CMDREQ_COMMAND"
F_CMDREQCMDARG = "CMDREQ_COMMAND_ARGS"

def parseline(pline, fileformat=227):
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

    ret[F_CMDREQINDEX] = pline[0]
    ret[F_CMDREQCMDNAME] = pline[1]
    ret[F_CMDREQCMDARG] = pline[2]

    return ret