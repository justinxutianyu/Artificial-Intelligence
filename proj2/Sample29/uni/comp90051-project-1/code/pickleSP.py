import geninst
import cPickle

TRAIN = "../data/train_pickle.pkl"

def loadAdjacencyList(filename):
    return cPickle.load(open(filename))

def main():

    print("Loading data")
    training = loadAdjacencyList(TRAIN)
    print("Finding lengths")
    spaths = geninst.shortestPath(training)
    print("Storing data")
    cPickle.dump(spaths, open(data/train_sp_pickle.pkl, 'wb'))


if __name__ == "__main__":
    main()
