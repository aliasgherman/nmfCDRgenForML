import numpy as np

F_TIME = "TIMESTAMP"
F_EVENT = "EVENTTYPE"
F_EVENTNAME = "EVENTNAME"
F_NUMCONTEXT = "NUMOFCONTEXT"
F_CONTEXTS = "CONTEXTIDS"
F_INVALID_INT = -919191



def convTypes(values, types):
    if ((types == int) or (types == float)) and (values.strip() == ''):
        return np.nan
    elif types == str:
        return values
    else:
        return types(values)



def processSets(pline, setHeader, setTypes, customPrefDict, idxCustomDictPara,
                idxNumSets, idxParamsPerSet, keepCountForDict=False):
    ret = {}
    '''

    :param pline:
    :param setHeader:
    :param setTypes:
    :param customPrefDict: should be like {0 : "PCELL", 1: "SCELL 1" etc}
    :param idxCustomDictPara: is the index of the pline to lookup the customPrefDict
    :param idxNumSets:
    :param idxParamsPerSet:
    :param keepCountForDict: If you supply a customPrefixDict then you donot want to append the counters in most cases. This is to still write prefixes and add the Loop counter in the header name
    :return:
    '''

    if idxNumSets == None:
        numSets = 1 #there are no sets to loop through. Just run the loop once in this case.
        paramsPerSet = idxParamsPerSet #if numSets is set to None, then total params have to be specified in this argument
    else:
        try:
            numSets = int(pline[idxNumSets])
        except:
            return {} , '' #something is wrong determining the number of sets.
        paramsPerSet = int(pline[idxParamsPerSet])
        pline = pline[1 + max(idxNumSets,idxParamsPerSet):] #discard the number of sets and param per set information now

    setHeader = setHeader[:paramsPerSet] #discard excessive headers for older file formats

    if customPrefDict != None: #no custom prefixes are defined
        prefCounts = {x + "_":0 for x in customPrefDict.values()} #maintain a count of prefixes (like ACTIVECELL 0, 1, 2...
        prefCounts["UNK"] = 0 #add a field for unknowns

        for i in range(numSets):
            hCItems = pline[0: paramsPerSet]
            hCItems = [convTypes(hCItems[x], setTypes[x]) for x in range(0, len(hCItems))]
            cT = pline[idxCustomDictPara]
            if cT in customPrefDict.keys():
                preF = customPrefDict[cT] + "_"
            else:
                preF = "UNK_"
            prefCounts[preF] += 1
            if keepCountForDict: #should be False in most cases.
                ret.update(dict(zip([preF + x + "_" + str(prefCounts[preF]) + "_" + str(i) for x in setHeader], hCItems)))
            else:
                ret.update(dict(zip([preF + x + "_" + str(prefCounts[preF]) for x in setHeader], hCItems)))
            pline = pline[paramsPerSet:]
    else:
        for i in range(numSets):
            hCItems = pline[0: paramsPerSet]
            hCItems = [convTypes(hCItems[x], setTypes[x]) for x in range(0, len(hCItems))]
            ret.update(dict(zip([x + "_" + str(i) for x in setHeader], hCItems)))
            pline = pline[paramsPerSet:]

    return ret, pline

