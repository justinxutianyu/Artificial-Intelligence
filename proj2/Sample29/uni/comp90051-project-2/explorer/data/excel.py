import pandas as pd
import os

from data import *
from openpyxl import load_workbook
from util import *

class VicHealth(Data):

    def __init__(self):
        self.data_source = "Excel"
        self.instances = []

    def add_instance(self, instance):
        self.instances.append(instance)

    #override
    def to_dataframe(self):
        data = {label:[] for label in self.instances[0].features.keys()}
        for instance in self.instances:
            for label,feature in instance.features.items():
                data[label].append(feature)
        return pd.DataFrame(
            data,
            index=[instance.name for instance in self.instances]
        )

class VicHealthExcel(Instance):

    def __init__(self, file):
        directory, filename = splitPath(file)
        name, extension = splitFileName(filename)
        self.name = name
        self.type = extension[1:]
        self.filename = filename
        self.directory = directory
        self.path = os.path.join(directory, filename)
        self.features = dict()

    def read_features(self):
        wb = load_workbook(self.path)
        sheet = wb.get_sheet_by_name("data")
        index_1 = fill_category_names(sheet.columns[0])
        index_2 = [cell.value for cell in sheet.columns[1]]
        columns = zip(index_1, index_2)
        values  = [cell.value for cell in sheet.columns[2]]
        self.features = dict( zip(columns, values) )

    #Override
    def to_series(self):
        return pd.Series(
            self.features,
            name=self.name
        )

    def clean_name(self):
        components = self.name.split("-")
        self.name  = "_".join(
            [c.strip().lower() for c in components[:-2]]
        )

    def clean_features(self, mappings):
        for category,features in mappings.items():
            for feature,mapping in features.items():
                #Build up a set of cleaned features
                old_name = (category[0], feature)
                new_name = (category[1], mapping[0])
                dtype = mapping[1]
                if dtype == "int":
                    self.features[new_name] = clean_integer(self.features[old_name])
                elif dtype == "float":
                    self.features[new_name] = clean_float(self.features[old_name])
                elif dtype == "string":
                    self.features[new_name] = clean_string(self.features[old_name])
                else:
                    raise Exception("""
                        Error cleaning {}.
                        Invalid data type - {}.
                    """.format(old_name, dtype)
                    )
                #Remove the original feature
                self.features.pop(old_name)

    def compute_distances(self):
        print(self.features[("geography", "location")])
        print(self.features[("community", "name")])



######################
# Cleaning Functions #
######################

def clean_integer(value):
    if value == "<5":
        return 0
    elif value == "n/a":
        return None
    else:
        return value

def clean_float(value):
    if value == "n/a":
        return None
    else:
        return value

def clean_string(value):
    return value

def fill_category_names(column):
    categories = []
    for cell in column:
        if cell.value:
            category = cell.value
        categories.append(category)
    return categories
