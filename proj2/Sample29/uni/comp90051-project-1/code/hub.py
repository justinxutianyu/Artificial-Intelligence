HUB_THRESHOLD = 0.025 # Percent

def parseAdjacencyList(filename):
    lengthDict = {}
    with open(filename) as file:
        lengthDict["highest"] = 0
        for line in file:
            node, length = getNodeLength(line)
            if length > lengthDict["highest"]:
                lengthDict["highest"] = length
            lengthDict[node] = length
    return lengthDict

def getNodeLength(adjacencyList):
    nodes = (node.strip() for node in adjacencyList.split("\t"))
    return int(nodes.next()), len(list(nodes))

def findHubs(lengthDict):
    hubDict = dict()
    hubCount = 0
    authorityCount = 0
    for k,v in lengthDict.items():
        if k != "highest":
            lengthPercent = (float(v) / float(lengthDict["highest"])) * 100
            if lengthPercent > HUB_THRESHOLD:
                hubCount += 1
                hubDict[k] = (v, True, lengthPercent)
            else:
                authorityCount += 1
                hubDict[k] = (v, False, lengthPercent)
    return hubDict, hubCount, authorityCount

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

def main():
    #Crunch the numbers
    lengths = parseAdjacencyList("../data/train.txt")
    hubs, hubCount, authorityCount = findHubs(lengths)

    #Print some stats
    print("Found {} hubs, {} authorities".format(hubCount, authorityCount))
    i = 1
    for hub in sorted(hubs.values(), key=lambda n: n[0], reverse=True):
        if i > 10:
            break
        print("{}. length - {}, length percent - {}, hub - {}".format(i, hub[0], hub[2], hub[1]))
        i += 1

    #Parse the test file
    testData = parseTest("../data/test-public.txt")

    #Write the predicitons file
    output = open("predictions.csv", "w")
    output.write("Id,Prediction\n")
    for k,v in testData.items():
        if hubs[v[0]][1]:
            output.write("{},{}\n".format(k, 1.0))
        else:
            output.write("{},{}\n".format(k, 0.0))
    print("Results written to predictions.csv")

if __name__ == "__main__":
    main()
