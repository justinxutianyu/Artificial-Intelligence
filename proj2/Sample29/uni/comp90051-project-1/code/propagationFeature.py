#allows for a simple page-rank / multi level neighbour derivative to be called
#without degredation of node values, looping means it cant go back and loop through already seen nodes
def propagateImportance(node, adjDict = {}, initialWeighting = 2, maxDepth = 1, looping = False):
    openList = []
    fronteirList = []
    closedDict = {}
    if(adjDict.has_key(node)):
        for item in adjDict[node]:
            openList.append(item)
            closedDict[item] = 1.0 / initialWeighting
        maxDepth -= 1
        initialWeighting += initialWeighting
        while(maxDepth > 0 and len(openList) > 0):
            for item in openList:
                if(adjDict.has_key(item)):
                    for item2 in adjDict[item]:
                        if(closedDict.has_key(item2)):
                            if(looping == True):
                                fronteirList.append(item2)
                            closedDict[item2] += 1.0 / initialWeighting
                            continue
                        else:
                            closedDict[item2] = 1.0 / initialWeighting
                        fronteirList.append(item2)
            maxDepth -= 1
            initialWeighting += initialWeighting
            openList = fronteirList
            fronteirList = []
        for item in closedDict:
            fronteirList.append((item, closedDict[item]))
        return fronteirList
    return fronteirList


def listIntersection(listA, listB):
    returnList = []
    lookupDict = {}
    for item in listA:
        lookupDict[item] = 1
    for item in listB:
        if(lookupDict.has_key(item)):
            returnList.append(item)
    return returnList

def buildCluValList(listOfPairs, list):
    tmpList = []
    dict = {}
    for item2 in listOfPairs:
        dict[item2[0]] = item2[1]
    for item in list:
        if(dict.has_key(item)):
            tmpList.append(dict[item])
    return tmpList


def forwardPropagationIntersection(source, target, training, depth, looping):
    src = propagateImportance(source,training,1,depth, looping)
    dst = propagateImportance(target,training,1,depth, looping)
    #print src
    #print dst
    srcL = []
    dstL = []
    for node,weight in src:
        srcL.append(node)
    for node,weight in dst:
        dstL.append(node)
    intersection = listIntersection(srcL,dstL)
    x = len(srcL) - len(intersection)
    y = len(dstL) - len(intersection)
    z = x + y + len(intersection)
    absVal = str(float(len(intersection) + 1)/(1 + z))


    srcInter = buildCluValList(src, intersection)
    dstInter = buildCluValList(dst, intersection)
    C = sum(srcInter)/(len(src) + 0.1) + sum(dstInter)/(len(dst)+ 0.1)
    val = 0.0
    count = 0
    tupDict = {}
    for item in src:
        tupDict[item[0]] = item[1]
    for item in dst:
        if(tupDict.has_key(item[0])):
            val += tupDict[item[0]] * item[1]
            count += 1
    val = val / (count + 0.01)
    return val

def test():
    import cPickle
    import random
    import time

    print("Loading data")
    TRAIN = "../data/train_pickle.pkl"
    outgoingNodes = cPickle.load(open(TRAIN))

    print("Sampling edge")
    source = random.sample(outgoingNodes.keys(), 1)[0]
    target = random.sample(outgoingNodes[source], 1)[0]

    print("Computing feature")
    start = time.time()
    propagationIntersection = forwardPropagationIntersection(
        int(source), int(target), outgoingNodes, depth=2, looping=True
    )
    end = time.time()
    total = end - start

    return propagationIntersection, total

if __name__ == "__main__":
    val, time = test()
    print("Computed {} in {} seconds".format(val, time))
