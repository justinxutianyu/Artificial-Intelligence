import pandas as pd
import os

from data import *
from nltk.corpus import stopwords
from string import punctuation, maketrans

STOPWORDS = set(stopwords.words("english"))

class Collection(Data):

    def add_instance(self, document):
        if not self.data_source:
            self.data_source = document.directory
        else:
            if document.directory != self.data_source:
                raise ValueError("""
                    Tried to insert document from: {}\n
                    Expected document from: {}\n
                    This won't work because all instances must
                    be stored in the same directory.
                """)
        self.instances = self.instances.append(document.features)
        self.instances.fillna(0, inplace=True)

class Document(Instance):

    def __init__(self, file):
        directory, filename = splitPath(file)
        name, extension = splitFileName(filename)
        self.name = name
        self.type = extension[1:]
        self.filename = filename
        self.directory = directory
        self.path = os.path.join(directory, filename)
        self.features = pd.Series(name=self.name)

    def computeDocLength(self):
        doclength = DocLength()
        doclength.compute(self)
        self.addFeature(doclength)

    def computeTermFrequency(self):
        frequencies = dict()
        with open(self.path) as file:
            for line in file:
                for token in tokenize(line, STOPWORDS):
                    if token in frequencies.keys():
                        frequencies[token].value += 1
                    else:
                        frequencies[token] = TermFrequency(token)
                        frequencies[token].value += 1
        for token,feature in frequencies.items():
            self.features[token] = feature.value

class DocLength(Feature):

    def __init__(self):
        self.name  = "length"
        self.value = 0

    def compute(self, document):
        with open(document.path) as file:
            for line in file:
                self.value += len(line)

class TermFrequency(Feature):

    def __init__(self, term):
        self.name = term
        self.value = 0

    def increment(self):
        self.value += 1


####################
# Helper Functions #
####################

def splitFileName(filename):
    return os.path.splitext(filename)

def splitPath(filename):
    return os.path.split(os.path.abspath(filename))

def tokenize(string, stopwords=[]):
    """
    Tokenizes a string.
    """
    string     = string.translate(None, punctuation)
    string     = string.lower()
    return (
        token for token in string.split()
        if token not in stopwords
    )
