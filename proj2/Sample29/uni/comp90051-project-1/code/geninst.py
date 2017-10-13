"""
Classifier Wrapper Functions

Author: Kai Hirsinger (kai.hirsinger@gmail.com)
        Aleck MacNally (amacnally@student.unimelb.edu)
        Perren Spence (pspence@student.unimelb.edu)
Since:  11th August 2015

Generates instances
"""

import random

from graph import Graph
from peerConnections import commonInterest, adamicAdar
from propagationFeature import forwardPropagationIntersection
from intersect import nodesInterestedIn, isInterestedIn, jaccard
from sys import stdout

def genInstances(edges, train_outgoing, train_incoming, label) :
    """
    Generates a set of instances from a dictionary
    of edges. Instances are returned as a list of
    dicts, with each dict representing a separate
    instance.
    """
    instances = []
    c = 0
    total = len(edges.items())
    #done, total = 0, len(edges.items())
    for source,targets in edges.items():
        #displayProgressBar(done, total)
        #done += 1

        for target in targets:
            print("Doing edge {}|{}".format(source, target))
            c += 1
            instances.append(
                getFeatures(source, target, train_outgoing, train_incoming, label)
            )
        print (float(c)/(1 + total))
    return instances

# TODO - add more features and fix up somehow shortes path
def getFeatures(source, target, train_outgoing, train_incoming, label):

    features = {}

    edge = str(source) + "|" + str(target)
    features["edge"] = edge

    #To save on computation, we only compute the shortest path
    #for nodes in the test data
    print("Computing: spath")
    if label == True:
        shortestPath = 1
    else:
        shortestPath = getShortestPath(
            source, target, train_outgoing, 3
        )
    features["spath"] = shortestPath

    #The number of edges directed away from the source node
    print("Computing: in_hub_score")
    hubScore = len(isInterestedIn(source, train_outgoing))
    features["in_hub_score"] = hubScore

    #The number of edges directed into the source node
    print("Computing: in_auth_score")
    authScore = len(nodesInterestedIn(source, train_incoming))
    features["in_auth_score"] = authScore

    #The number of edges directed away from the source node
    print("Computing: out_hub_score")
    hubScore = len(isInterestedIn(target, train_outgoing))
    features["out_hub_score"] = hubScore

    #The number of edges directed into the source node
    print("Computing: out_auth_score")
    authScore = len(nodesInterestedIn(target, train_incoming))
    features["out_auth_score"] = authScore

    #Jaccard similarity between the incoming/outgoing sets
    print("Computing: Jaccard")
    intersection, union, jaccardSim = jaccard(source, target, train_outgoing)
    features["jaccard"] = jaccardSim
    features["intersection"] = intersection
    features["union"] = union

    #Weird Perren feature #1
    #print("Computing: Density")
    #density = commonInterest(source, target, train_outgoing, train_incoming)
    #features["density"] = density

    print("Computing: Adamic Adar")
    adamicAdarian = adamicAdar(source, target, train_outgoing, train_incoming)
    features["AA"] = adamicAdarian

    #Weird Perren feature #2
    #print("Computing: Propagation\n")
    #propagationIntersection = forwardPropagationIntersection(
    #    int(source), int(target), train_outgoing, depth=2, looping=False
    #)
    #features["propagation"] = propagationIntersection

    #The nodes comprising the edge
    #features["source"] = int(source)
    #features["target"] = int(target)

    features["label"] = label

    return features

def getShortestPath(source, target, train_outgoing, max_path_length=10):
    """
    Gets the shortest path between two nodes by means of a
    breadth first search. If the path cannot be found within
    max_path_length iterations of the search, it is set to a
    pre-defined maximum value.
    """
    return Graph(train_outgoing).shortestPathLength(
        source, target, max_path_length
    )

def shortestPath(vertices) :

    dist = dict()
    maxSize = len(vertices)

    for s1 in vertices.keys() :
        for s2 in vertices.keys() :
            dist[str(s1) +"|" + str(s2)] = maxSize

    for s1 in vertices.keys() :
        dist[str(s1) +"|"+ str(s1)] = 0
        for link in vertices[s1] :
            dist[str(s1) + "|"+ str(link)] = 1


    for k in vertices.keys() :
        for i in vertices.keys() :
            for j in vertices.keys() :
                if dist[str(i) + "|" + str(j)] > dist[str(i) + "|" + str(k)] + dist[str(k) + "|" + str(j)] :
                    dist[str(i) + "|" + str(j)] = dist[str(i) + "|" + str(k)] + dist[str(k) + "|" + str(j)]

    return dist

def displayProgressBar(done, total):
    progress = int(float(done) / float(total) * 100)
    stdout.write("\r{0}% Complete".format(str(progress)))
    stdout.flush()

#For testing only
def main():
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
    print("Source: {}".format(source))
    print("Target: {}".format(target))
    start_time = time.time()
    features = getFeatures(
        source=source,
        target=target,
        train_outgoing=outgoingNodes,
        train_incoming={},
        label=None
    )
    end_time = time.time()
    print(features)
    print("Computed in {} seconds".format(end_time - start_time))

if __name__ == "__main__":
    main()
