"""
Contains classes and functions for representing
data to machine learning classifiers.

Author: Kai Hirsinger (kai.hirsinger@gmail.com)
Since:  18th September 2015
"""

import pandas as pd
import cPickle

class Data(object):
    """
    Generic class for representing data sets.

    Every data set has a data source and a collection
    of instances.

    data source - some piece of information indicative
                  of where the data came from (eg: a directory).

    instances   - a dictionary of name, object pairs.
                  The name is the name attribute of the
                  instance object, and the object is the
                  instance object itself.
    """

    def __init__(self):
        self.data_source = None
        self.instances = dict()

    def add_instance(self, instance):
        self.instances[instance.name] = instance

    def remove_instance(self, instance):
        self.instances.pop(instance.name)

    def to_pickle(self, pickle):
        file = open(pickle, "wb")
        cPickle.dump(self, file)

    def from_pickle(self, pickle):
        file = open(pickle)
        self = cPickle.load(file)

    def to_dataframe(self):
        df = pd.DataFrame()
        df.df_name = self.data_source
        for key,instance in self.instances.items():
            df = df.append(instance.to_series())
        return df

    def from_dataframe(self, dataframe):
        self.data_source = dataframe.df_name
        for row in dataframe.index:
            instance = Instance()
            self.instances[row] = instance.from_series(
                dataframe.loc[row]
            )

class Instance(object):

    def __init__(self, name):
        self.name = name
        self.features = dict()

    def addFeature(self, feature):
        self.features[feature.name] = feature

    def removeFeature(self, feature):
        self.features.pop(feature.name)

    def to_series(self):
        return pd.Series(self.features, name=self.name)

    def from_series(self, series):
        self.name = series.name
        self.features = dict(series)

class Feature(object):

    def __init__(self):
        self.name  = str()
        self.value = int()

    def compute(self):
        return self.value
