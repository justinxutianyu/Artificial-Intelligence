def additiveBlend(source = 0.0,dest = 0.0):
    return (1.0 - (1.0 - float(source)) * (1.0 - float(dest)))
from intersect import listIntersection
import math
def commonInterestNew(source, target, outgoingNodes, incomingNodes):
    itemsOfT = []
    itemsofS = []
    score = 0
    #things interested in the target
    if(incomingNodes.has_key(target)):
        itemsOfT = incomingNodes[target]
    #Of the items, see if they connect to themselves
    for item in itemsOfT:
        if(outgoingNodes.has_key(item)):
            itemsofS = outgoingNodes[item]
            score += len(listIntersection(itemsOfT, itemsofS))
    print "Connected Weight of target: ", score
    return score

def commonInterest(source, target, outgoingNodes, incomingNodes):
    #find all nodes of target.
    originalNodes = {}
    score = 0
    if(incomingNodes.has_key(target)):
        for item in incomingNodes[target]:
            originalNodes[item] = 0
    for item in originalNodes:
        #does this item go to any of the other original nodes, if so then increment score
        if(outgoingNodes.has_key(item)):
            #peers
            for item2 in outgoingNodes[item]:
                if(outgoingNodes.has_key(item2)):
                    #check if the peers go to originals
                    score += len(listIntersection(originalNodes, outgoingNodes[item2]))
                    #for other in originalNodes:
                    #    if(other in outgoingNodes[item2]):
                    #        score += 1
                    #        break
    fscore = 0.0
    #now check how many of the source connections are the peers.
    val = (float(score)/float(len(originalNodes) + 1))
    if(outgoingNodes.has_key(source)):
        for item in outgoingNodes[source]:
            if(originalNodes.has_key(item)):
                fscore = additiveBlend(fscore, val)
    return fscore

def adamicAdar(source, target, outgoingNodes, incomingNodes):
    listOfA = []
    listOfB = []
    if(outgoingNodes.has_key(source)):
        listOfA = listOfA + outgoingNodes[source]
    if(outgoingNodes.has_key(target)):
        listOfB = listOfB + outgoingNodes[target]
    if(incomingNodes.has_key(source)):
        listOfA = listOfA + incomingNodes[source]
    if(incomingNodes.has_key(target)):
        listOfB = listOfB + incomingNodes[target]

    listOfZs = listIntersection(listOfA, listOfB)
    val = 0
    for item in listOfZs:
        size = 0
        if(outgoingNodes.has_key(item)):
            size += len(outgoingNodes[item])
        if(incomingNodes.has_key(item)):
            size += len(incomingNodes[item])
        val += 1.0/(1 + math.log(size + 1))
    return val

def commonInterest2(source, target, outgoingNodes, incomingNodes):
    #find all nodes of target.
    originalNodes = {}
    score = 0
    if(incomingNodes.has_key(target)):
        for item in incomingNodes[target]:
            originalNodes[item] = 0
    for item in originalNodes:
        #does this item go to any of the other original nodes, if so then increment score
        if(outgoingNodes.has_key(item)):
            #peers
            for item2 in outgoingNodes[item]:
                if(outgoingNodes.has_key(item2)):
                    #check if the peers go to originals
                    for other in originalNodes:
                        if(other in outgoingNodes[item2]):
                            score += 1
                            break
    fscore = 0.0
    #now check how many of the source connections are the peers.
    val = (float(score)/float(len(originalNodes) + 1))
    if(outgoingNodes.has_key(source)):
        for item in outgoingNodes[source]:
            if(originalNodes.has_key(item)):
                fscore = additiveBlend(fscore, val)
    return fscore

def test():
    import cPickle
    import random

    import time

    INVERTED_TRAIN = "../data/train_inverted.pkl"
    TRAIN = "../data/train_pickle.pkl"

    print("Loading data")
    outgoingNodes = cPickle.load(open(TRAIN))
    incomingNodes = cPickle.load(open(INVERTED_TRAIN))

    print("Sampling edges")
    source = random.sample(outgoingNodes.keys(), 1)[0]
    target = random.sample(outgoingNodes[source], 1)[0]

    print("Computing fscore")
    start = time.time()
    fscore = commonInterest(source, target, outgoingNodes, incomingNodes)
    end = time.time()
    diff = end - start

    return fscore, diff

if __name__ == "__main__":
    feature, time = test()
    print("Computed {} in {} seconds".format(feature, time))
