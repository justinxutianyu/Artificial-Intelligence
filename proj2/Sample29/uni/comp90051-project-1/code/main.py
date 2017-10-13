import cPickle
import numpy as np
import pandas as pd
import random

from geninst import genInstances, getFeatures
from classifier import train, plot_learning_curve
from sklearn.metrics import classification_report
from time import time

TEST  = "../data/test-public.txt"
INVERTED_TRAIN = "../data/train_inverted.pkl"
TRAIN = "../data/train_pickle.pkl"
TRAINSP = "../data/train_sp_pickle.pkl"

TRAIN_INSTANCES = "../data/train_instances_pref.pkl"
TEST_INSTANCES = "../data/test_instances_pref.pkl"

FEATURES = [
    #"in_hub_score",
    #"in_auth_score",
    #"out_hub_score",
    #"out_auth_score",
    "jaccard",
    #"intersection",
    #"union",
    #"density",
    #"spath",
    #"propagation",
    #"preferential_attachment",
    #"source",
    #"AA",
    #"target"
]

REPORTING_DIR = "../predictions/classifier_report/"
PREDICTIONS_DIR = "../predictions/"

def loadAdjacencyList(filename):
    return cPickle.load(open(filename))

def countEdges(train):
    """
    Counts the edges in the training data
    Spoiler alert: there's lots and lots =)
    """
    numEdges = 0
    for k,v in training.items():
        print("Doing node {}".format(k))
        numEdges += 1 + len(v)
    return numEdges

def parseTest(filename):
    adjDict = dict()
    idDict  = dict()
    with open(filename) as file:
        next(file)
        for line in file:
            data = (field.strip() for field in line.split("\t"))
            _id   = int(data.next())
            _from = int(data.next())
            _to   = int(data.next())
            adjDict[_from] = [_to]
            idDict[str(_from) + "|" + str(_to)] = _id
    return adjDict, idDict

def sampleDict(adjDict, numSamples):
    keys = random.sample(adjDict, numSamples)
    sampleDict = {}
    for k in keys:
        if (adjDict[k] != []):
            sampleDict[k] = random.sample(adjDict[k], 1)
        #Pick a new key if this one's a dud
        else:
            new_k = random.sample(adjDict, 1)[0]
            keys.append(new_k)
            continue
    return sampleDict

def checkTest(source, target, test):
    """
    Checks if an edge exists in the test data
    """
    try:
        return test[source] == [target]
    except KeyError:
        return False

def createFalses(training, test, n):
    falses = {}
    i = 0
    while i < n :
        n1 = random.sample(training.keys(), 1)[0]
        n1list = training[n1] + [n1]
        n2 = random.sample(
            [v for v in training.keys() if v not in n1list], 1
        )[0]
        if n1 not in falses.keys():
            falses[n1] = [n2]
            i += 1
        elif n2 not in falses[n1]:
            falses[n1].append(n2)
            i += 1
        else:
            continue

    return falses

def genTrainingData(train_outgoing, train_incoming, test, n_true, n_false, outfile="../data/train_instances.pkl"):
    print("Sampling training data")
    sampledTrue  = sampleDict(train_outgoing, n_true)
    sampledFalse = createFalses(train_outgoing, test, n_false)

    print("Generating instances for training data")
    trues  = genInstances(sampledTrue, train_outgoing, train_incoming, True)
    falses = genInstances(sampledFalse, train_outgoing, train_incoming, False)

    trainData = pd.DataFrame(trues + falses)
    trainData.to_pickle(outfile)

    return trainData

def genTestData(train_outgoing, train_incoming, test, outfile="../data/test_instances.pkl"):
    print("Generating instances for test data")
    instances = pd.DataFrame(
        genInstances(test, train_outgoing, train_incoming, None)
    )
    instances.to_pickle(outfile)
    return instances

def classify(train_x, train_y, test, params=None):
    #Parameters used during cross validation
    if not params:
        params = {
            #"clf__fit_intercept":([True, False]),
            #"clf__C":([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
            #"clf__alpha":([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        }

    #Train the classifer and make some predictions
    clf = train(train_x, train_y, params)
    predictions = clf.predict_proba(
        test[[col for col in FEATURES]]
    )

    #Assign the predictions to the test data
    test["label"] = [
        prediction[1]
        for prediction in predictions
    ]

    return test, clf

def cv_report(clf, x, y, report_directory, report_name):
    report = open(report_directory + report_name + ".html", "w")
    report.write("<html>")

    learning_curve = plot_learning_curve(
        estimator=clf.estimator,
        title="Learning Curve",
        X=x,
        y=y,
        ylim=None,
        cv=None,
        n_jobs=1,
        train_sizes=np.linspace(.1, 1.0, 5)
    )
    learning_curve_file = report_directory + report_name + "_learning_curve.png"
    learning_curve.savefig(learning_curve_file)
    report.write("<img src={}></img>".format(report_name + "_learning_curve.png"))

    report.write("</html>")
    report.close()

PREBAKED = False
def main():
    #If we're generating instances from scratch
    test_outgoing, testIdLookup = parseTest(TEST)
    if not PREBAKED:
        print("Generating instances")
        train_outgoing = loadAdjacencyList(TRAIN)
        train_incoming = loadAdjacencyList(INVERTED_TRAIN)

        #train = genTrainingData(train_outgoing, train_incoming, test_outgoing, n_true=2, n_false=2)
        test  = genTestData(train_outgoing, train_incoming, test_outgoing)
        #TODO:This should only be uncommented if we don't want to compute the
        #test data
        train = pd.read_pickle(TRAIN_INSTANCES)

    #If we're loading pre-baked instances
    if PREBAKED:
        print("Loading instances from {}, {}".format(TRAIN_INSTANCES, TEST_INSTANCES))
        train = pd.read_pickle(TRAIN_INSTANCES)
        test  = pd.read_pickle(TEST_INSTANCES)

    print("Classifying")
    train_x = train[[col for col in FEATURES]]
    train_y = train["label"]
    classified, clf = classify(train_x, train_y, test)

    print("Generating stats")
    report_name = "{}_{}".format(
        int(time()),
        "report" #This should be the classifer name
    )
    #cv_report(clf, train_x, train_y, REPORTING_DIR, report_name)

    predictions_file = PREDICTIONS_DIR + "classified.csv"
    outfile = open(predictions_file, 'w')
    outfile.write("Id,Prediction\n")
    for edge,id in testIdLookup.items():
        prediction = float(classified[classified["edge"] == edge]["label"])
        outfile.write("{},{}\n".format(id, prediction))
    outfile.close()

    print("All done, results written to:")
    print("{} - Classifier metrics".format(report_name))
    print("{} - Kaggle predictions".format(predictions_file))
    print("Classifier metrics:")
    print("Accuracy: {}".format(clf.best_score_))

if __name__ == "__main__":
    main()
