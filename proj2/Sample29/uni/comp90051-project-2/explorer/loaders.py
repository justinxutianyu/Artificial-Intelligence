from config import *
from data.excel import *
from data.util import *

import os

class Loader(object):

    def __init__(self):
        self.directory = None
        self.data_set  = None

    def load_data(self):
        self.data_set = None

class Project2Data(Loader):

    def __init__(self):
        self.directory = os.path.abspath("./explorer/data_sets/project2_data")
        self.data_set  = None

    def load_data(self):
        data = VicHealth()
        crawler = Crawler()
        crawler.set_type("xlsx")
        files = crawler.crawl(self.directory)
        for file in files:
            instance = VicHealthExcel(file)
            instance.read_features()
            data.add_instance(instance)
        self.data_set = data

    def clean_data(self):
        if not(self.data_set):
            raise Exception("No data loaded - nothing to clean!")
        for instance in self.data_set.instances:
            instance.clean_name()
            instance.clean_features(
                mappings=PROJ2_MAPPINGS
            )
            instance.compute_distances()

    def to_dataframe(self):
        return self.data_set.to_dataframe()
