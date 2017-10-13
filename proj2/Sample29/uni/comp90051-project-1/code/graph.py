from sys import stdout

import cPickle
import json

TESTEDGE = 2

###########
# Classes #
###########

class Graph:

    def __init__(self, dict={}):
        self.nodes = dict

    def fromDict(self, dictionary):
        self.nodes = {
            source:(targets)
            for source, targets in dictionary.items()
        }
    
    def fromAdjacencyPkl(self, pklFile):
        with open(pklFile) as file:
            graph = cPickle.load(file)
            self.nodes = {
                source:targets
                for source, targets in graph.items()
            }

    def addPath(self, path):
        for i in range(0, len(path) - 1):
            if path[i] in self.nodes.keys():
                self.nodes[path[i]].append(path[i+1])
            else:
                self.nodes[path[i]] = [path[i+1]]

    def toJson(self, jsonFile):
        graph = dict()
        graph["nodes"] = []
        graph["links"] = []
        for source, targets in self.nodes.items():
            #Add the source to the nodelist
            sourceDict = {"name":str(source)}
            if sourceDict not in graph["nodes"]:
                graph["nodes"].append(sourceDict)
            for target in targets:
                #Add the target to the nodelist
                targetDict = {"name":str(target)}
                if targetDict not in graph["nodes"]:
                    graph["nodes"].append(targetDict)
                #Add the edge
                sourceIndex = findDictByValue(
                    graph["nodes"], "name", str(source)
                )
                targetIndex = findDictByValue(
                    graph["nodes"], "name", str(target)
                )
                graph["links"].append( {
                    "source" : sourceIndex,
                    "target" : targetIndex
                } )
        #Dump everything to JSON
        outfile = open(jsonFile, 'wb')
        json.dump(graph, outfile)

    def shortestPathLength(self, start, target, max_path_length=10):
        """
        Yields the shortest past in the
        graph between two nodes. Returns
        a default maximum value if the
        search expands beyond a certain
        value (set by the max_path_length
        parameter).
        """
        queue = [(start, 0)]
        while queue:
            node, path_length = queue.pop(0)
            #If the path is too long then stop
            if path_length >= max_path_length:
                return 10
            try:
                for adjacent in self.nodes[node]:
                    if adjacent == target:
                        return path_length + 1
                    else:
                        queue.append(
                            (adjacent, path_length + 1)
                        )
            except KeyError:
                continue

####################
# Helper Functions #
####################

def findDictByValue(list, key, value):
    """
    Finds the index of a dictionary in a list of
    dictionaries where the value of a key is set
    to some value.

    Example:
    In:
    list  = [{"name":"bob"}, {"name":"wendy"}, {"name":randy}]
    key   = "name"
    value = "wendy"

    Out: 1 (integer)
    """
    return list.index(
        filter(
            lambda dict: dict[key] == value,
            list
        )[0]
    )

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
    print("Graphing training data")
    train = Graph()
    train.fromAdjacencyPkl("../data/train_pickle.pkl")
    print("Reading test data")
    test = parseTest("../data/test-public.txt")
    print("Finding paths for test edge {}".format(TESTEDGE))
    pathGraph = Graph()
    _id, _from, _to = TESTEDGE, test[TESTEDGE][0], test[TESTEDGE][1]
    i = 0
    for path in train.breadthFirst(_from, _to):
        if path:
            i += 1
            print("Adding path {}".format(path))
            pathGraph.addPath(path)
            if i > 5:
                break
        #else:
            #print("Null path!")
    print("Dumpting to JSON")
    pathGraph.toJson("test_{}.json".format(TESTEDGE))
    print("Finished!")

    #test = {
    #    "Andy":["Bob", "Wendy"],
    #    "Wendy":["Steve"],
    #    "Bob":["Steve"],
    #    "Steve":[]
    #}
    #myGraph.fromDict(test)
    #myGraph.toJson("before.json")
    #path = ["Steve", "Andy", "Steve"]
    #myGraph.addPath(path)
    #yGraph.toJson("after.json")

if __name__ == "__main__":
    main()
