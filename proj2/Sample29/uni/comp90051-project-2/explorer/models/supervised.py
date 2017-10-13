import cPickle

from sklearn.linear_model import *

class SupervisedModel(object):

    def __init__(self):
        self.data = None
        self.metrics = None
        self.base_model = None
        self.trained_model = None
        self.parameters = None

    def set_model(self, model):
        self.model = model

    def train(self):
        return None

    def predict(self):
        return None

    def compute_metrics(self):
        return None

    def cv_params(self):
        return None

    def dump_pickle(self, dest_file):
        cPickle.dump(self, open(dest_file, 'wb'))

    def load_pickle(self, pickle):
        self = cPickle.load(open(pickle))

class SKLearnSupervisedModel(SupervisedModel):

    def train(self):
        self.model.fit(self.data.data, self.data.labels)

    def predict(self, data):
        data.labels = self.model.predict(data.data)
        return data

    def compute_metrics(self):
        return None

    def cv_params(self, cv=5, scoring="roc_auc", n_jobs=-1):
        pipeline = Pipeline([
            ("clf", self.model())
        ])
        grid_search = GridSearchCV(
            pipeline,
            self.params,
            scoring=scoring,
            cv=cv,
            n_jobs=n_jobs
        )
        grid_search.fit(data.data, data.labels)
        self.params = grid_search.best_params

class SKLearnLogisticRegression(SKLearnSupervisedModel):

    def __init__(self):
        self.data = None
        self.metrics = None
        self.base_model = LogisticRegression()
        self.trained_model = None
        self.parameters = {
            "clf__C":([float(n) for n in np.linspace(0,100,1001)]),
            "clf__fit_intercept":([True, False])
        }
