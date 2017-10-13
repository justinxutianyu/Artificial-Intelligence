import networkx as nx
import matplotlib.pyplot as plt

def GenerateGraph(nodes, edges, positions):
    plt.close()
    myGraph = nx.Graph()
    #create dictionaries:
    L = {}
    LoPo = {}
    LaPo = {}#label Positions
    i = 0
    myGraph.add_edges_from(edges)
    for node in nodes:
        L[i] = node
        LoPo[node] = positions[i]
        LaPo[i] = (positions[i][0],positions[i][1] + 1)
        i += 1
    myH = nx.relabel_nodes(myGraph, L)
    nx.draw(myH, LoPo)
    nx.draw_networkx_labels(myH, LaPo, L)
    print("Nodes of graph: ")
    print(myH.nodes())
    print("Edges of graph: ")
    print(myH.edges())
    #plt.show to show the file
    return myH



#dist is from center, NSWE is the cardinal directions, prefHospital is closest public hospital, names is the index...
def visualClusteringPrecompute(distance = [], NSWE = [], prefHospital = [], names = []):
    clusterBasedOnHospital = {}
    i = 0
    while(i < len(distance)):
        vdirection = (0,0)
        vstring = NSWE[i]
        #print vstring
        for dir in vstring:
            if(dir == 'W'):
                vdirection = (vdirection[0] - 1, vdirection[1])
            if(dir == 'E'):
                vdirection = (vdirection[0] + 1, vdirection[1])
            if(dir == 'N'):
                vdirection = (vdirection[0], vdirection[1] + 1)
            if(dir == 'S'):
                vdirection = (vdirection[0], vdirection[1] - 1)
        #print vdirection
        nsum = math.sqrt(vdirection[0] ** 2 + vdirection[1] ** 2)
        vdirection = (vdirection[0]/nsum, vdirection[1]/nsum)
        if(clusterBasedOnHospital.has_key(item)):
            clusterBasedOnHospital[item].append((names[i], distance[i], vdirection))
        else:
            clusterBasedOnHospital[item] = [(names[i], distance[i], vdirection)]
        i += 1
    #for item in clusterBasedOnHospital:
    #    print "\n", item
    #    for item2 in clusterBasedOnHospital[item]:
    #        print "\t", item2[0], "dist from melb: ", item2[1], "Km, in the direction of: ", item2[2]
    return clusterBasedOnHospital
