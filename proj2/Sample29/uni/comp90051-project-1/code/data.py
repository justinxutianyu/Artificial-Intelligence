"""
Data Wrapper Functions

Author: Kai Hirsinger
Since:  11th August 2015

Wrapper function for reading data provided
for project 1 in Statistical Machine Learning.
"""

import pandas as pd

from sys import stdout

class Graph:

    def __init__(self):
        self.nodes = []
        self.edges = []

    def fromAdjacencyListFile(self, filename):
        with open(filename) as file:
            for line in file:
                nodes = (int(n.strip()) for n in line.split("\t"))
                source = nodes.next()
                if source not in self.nodes:
                    self.nodes.append(source)
                for node in nodes:
                    edge = (source, node)
                    self.edges.append(edge)

    def fromAdjacencyMatrixFile(self, file):
        return None

    def toAdjacencyMatrix(self, file=None):
        return None

def parseAdjacencyList(filename):
    node_list = []
    i = 0
    for line in open(filename):
        if i < 2:
            node_line = (int(n.strip()) for n in line.split("\t"))
            node_list.append( (node_line.next(), [node for node in node_line]) )
            i += 1
        else:
            break
    return node_list

def addEdges(node_list):
    edge_list = dict()
    node_incomings = dict()
    # Populates incoming edge count for each node
    i = 1
    print("Populating incoming edge count")
    for node in node_list:
        name, tonodes = node[0], node[1]
        for tonode in tonodes:
            if tonode in node_incomings.keys():
                node_incomings[tonode] += 1
            else:
                node_incomings[tonode] = 1
    # Populates edge dict with outgoing for source, incoming for origin
    i = 1
    print("Building edge list")
    for node in node_list:
        displayProgressBar(i, len(node_list))
        i += 1
        name, tonodes = node[0], node[1]
        for tonode in tonodes:
            edge_list[(name, tonode)] = (len(tonodes), node_incomings[tonode], True)
    return edge_list

def addEdges_connections(node_list):
    edge_list = dict()
    node_incomings = dict()
    # Populates incoming edge count for each node
    i = 1
    print("Populating incoming edge count")
    for node in node_list:
        name, tonodes = node[0], node[1]
        for tonode in tonodes:
            if tonode in node_incomings.keys():
                node_incomings[tonode].append(name)
            else:
                node_incomings[tonode] = [name]
    # Populates edge dict with outgoing for source, incoming for origin
    i = 1
    print("Building edge list")
    for node in node_list:
        displayProgressBar(i, len(node_list))
        i += 1
        name, tonodes = node[0], node[1]
        for tonode in tonodes:
            edge_list[(name, tonode)] = (tonodes, node_incomings[tonode], True)
    return edge_list

def nodeDegrees(node):
    return degrees

def dumpAdjcacencyMatrixToCSV(graph):
    data = pd.DataFrame(
        index=graph["nodes"],
        columns=graph["nodes"]
    )
    for edge in graph["edges"]:
        source, dest = edge[0], edge[1]
        data.loc[source][dest] = 1
        data.loc[dest][source] = 1
    data = data.fillna(0)
    data.to_csv("adj_train.csv")

def displayProgressBar(done, total):
    progress = int(float(done) / float(total) * 100)
    stdout.write("\r{0}% Complete".format(str(progress)))
    stdout.flush()

def main():
    test = Graph()
    test.fromAdjacencyListFile("../data/test.txt")
    print(test.nodes)
    print(test.edges)
    #data_loc = "../data/train.txt"
    #print("Parsing data from file")
    #adjacencyList = parseAdjacencyList(data_loc)
    #print("Making edges")
    #instances = addEdges_connections(adjacencyList)
    #graph = graphFromFile(data_loc)
    #print("Generating adjacency matrix")
    #dumpAdjcacencyMatrixToCSV(graph)
    #print(instances)

if __name__ == "__main__":
    main()
