import pandas as pd

from data import *

class GraphEdge(Instance):

    def __init__(self, graph, edge):
        self.name = str(edge.source) + "|" + str(edge.target)
        self.edge = edge
        self.graph = graph
        self.features = pd.Series()

    def computeAdamicAdar(self):
        return self.graph.adamicAdar(self.edge)

    def computePropogation(self):
        return self.graph.propogation(self.edge)

    def computeJaccardSimilarity(self):
        return self.graph.jaccardSimilarity(self.edge)

    def computeHubScore(self):
        return self.graph.hubScore(self.edge)

    def computeAuthorityScore(self):
        return self.graph.adamicAdar(self.edge)
