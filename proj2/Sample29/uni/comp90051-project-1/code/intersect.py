import cPickle

from utility import parseAdjacencyList

OUTPUT_FILE = "intersect_predicitons.csv"
TEST  = "../data/test-public.txt"
TRAIN = "train_pickle.pkl"

def parseTest(filename):
    edgeDict = dict()
    with open(filename) as file:
        next(file)
        for line in file:
            data = (field.strip() for field in line.split("\t"))
            _id   = int(data.next())
            _from = int(data.next())
            _to   = int(data.next())
            edgeDict[_id] = (_from, _to)
    return edgeDict

def parseAdjacencyList(filename):
    return cPickle.load(open(filename))
    """nodeDict = {}
    with open(filename) as file:
        #i = 0
        for line in file:
            #if i > 1000:
                #break
            row = (int(field.strip()) for field in line.split("\t"))
            nodeDict[row.next()] = row
            #i += 1
    return nodeDict"""

def listIntersection(listA, listB):
    returnList = []
    lookupDict = {}
    for item in listA:
        lookupDict[item] = 1
    for item in listB:
        if(lookupDict.has_key(item)):
            returnList.append(item)
    return returnList

def nodesInterestedIn(node, nodeDict):
    interested = []
    for k in nodeDict:
        for kk in nodeDict[k]:
            if kk == node:
                interested.append(k)
                break
    return interested

def isInterestedIn(node, nodeDict):
    if(nodeDict.has_key(node)):
        return nodeDict[node]
    return []

def jaccard(source, target, nodeDict):
    interestsFrom = nodesInterestedIn(source, nodeDict)
    interestsTo   = nodesInterestedIn(target, nodeDict)
    commonInterests = listIntersection(interestsFrom, interestsTo)

    x = len(interestsFrom) - len(commonInterests)
    y = len(interestsTo) - len(commonInterests)
    union = x + y + len(commonInterests)

    jaccardSim = float(len(commonInterests)) / (float(union) + 1)

    return len(commonInterests), union, jaccardSim

def script():
    test  = parseTest(TEST)
    train = parseAdjacencyList(TRAIN)

    output = open(OUTPUT_FILE, "w")
    output.write("Id,Prediction\n")

    i = 0
    for k,v in test.items():
        if i > 5:
            break
        i += 1
        print("Doing number {}".format(i))
        nodeFrom = v[0]
        nodeTo = v[1]
        interestsFrom = nodesInterestedIn(nodeFrom, train)
        interestsTo = nodesInterestedIn(nodeTo, train)
        commonInterests = listIntersection(interestsFrom, interestsTo)
        print("Common interests = {}".format(commonInterests))

        x = len(interestsFrom) - len(commonInterests)
        y = len(interestsTo) - len(commonInterests)
        union = x + y + len(commonInterests)

        confidence = float(len(commonInterests)) / (float(union) + 1)

        output.write("{},{}\n".format(k, confidence))
    print("Results written to {}".format(OUTPUT_FILE))

def main():
    test  = parseTest(TEST)
    train = parseAdjacencyList(TRAIN)

    output = open(OUTPUT_FILE, "w")
    output.write("Id,Prediction\n")

    i = 0
    for k,v in test.items():
        #if i > 5:
        #    break
        i += 1
        print("Doing number {}".format(i))
        nodeFrom = v[0]
        nodeTo = v[1]
        interestsFrom = isInterestedIn(nodeFrom, train)
        interestsTo = nodesInterestedIn(nodeTo, train)
        commonInterests = listIntersection(interestsFrom, interestsTo)
        print("Common interests = {}".format(commonInterests))

        x = len(interestsFrom) - len(commonInterests)
        y = len(interestsTo) - len(commonInterests)
        union = x + y + len(commonInterests)

        confidence = float(len(commonInterests)) / (float(union) + 1)

        output.write("{},{}\n".format(k, confidence))
    print("Results written to {}".format(OUTPUT_FILE))

if __name__ == "__main__":
    main()
