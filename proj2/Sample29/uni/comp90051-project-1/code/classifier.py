"""
Classifier Wrapper Functions

Author: Kai Hirsinger (kai.hirsinger@gmail.com)
Since:  11th August 2015

Implements a wrapper function for the scikit-learn
classifiers.
"""

from sklearn import neighbors
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, BaggingClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import chi2, SelectKBest, VarianceThreshold
from sklearn.grid_search import GridSearchCV
from sklearn.learning_curve import learning_curve
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.cross_validation import cross_val_score

#This is just for testing
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def train(x, y, params):

    #Leave the classifer of choice uncommented
    pipeline = Pipeline([
        #("clf", RandomForestClassifier(
        #    criterion="entropy",
        #    n_estimators=200,
        #    n_jobs=-1,
        #    oob_score=True,
        #    max_features=None,
        #    max_leaf_nodes=4
        #))
        ("clf", BaggingClassifier(
            base_estimator=LogisticRegression(
                penalty="l1",
                #class_weight="auto",
                C=100.0
            ),
            n_estimators=10,
            n_jobs=1,
            #max_samples=0.5
        ))
        #("clf", LogisticRegression(
        #    penalty="l1",
        #    class_weight="auto",
        #    C=1.0
        #))
        #("clf", SVC(
        #    probability=True,
        #    kernel="linear"
        #))
        #("clf", MultinomialNB())
    ])

    #Cross-validate the chosen classifer
    grid_search = GridSearchCV(
        pipeline, params,
        scoring="recall",
        #cv=5,
        n_jobs=-1,
        #iid=False
    )

    #Fit the cross-validated classifier and return it
    grid_search.fit(x, y)
    return grid_search

def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    """
    Generate a simple plot of the test and traning learning curve.

    Parameters
    ----------
    estimator : object type that implements the "fit" and "predict" methods
        An object of that type which is cloned for each validation.

    title : string
        Title for the chart.

    X : array-like, shape (n_samples, n_features)
        Training vector, where n_samples is the number of samples and
        n_features is the number of features.

    y : array-like, shape (n_samples) or (n_samples, n_features), optional
        Target relative to X for classification or regression;
        None for unsupervised learning.

    ylim : tuple, shape (ymin, ymax), optional
        Defines minimum and maximum yvalues plotted.

    cv : integer, cross-validation generator, optional
        If an integer is passed, it is the number of folds (defaults to 3).
        Specific cross-validation objects can be passed, see
        sklearn.cross_validation module for the list of possible objects

    n_jobs : integer, optional
        Number of jobs to run in parallel (default 1).
    """
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

#This is just for testing
def main():
    data = pd.DataFrame(
        np.random.randint(0,10, (20,4)),
        columns = ["a", "b", "c", "d"]
    )
    data["label"] = [
        True, False, False, True, False,
        True, False, False, True, False,
        True, False, False, True, False,
        True, False, False, True, False,
    ]
    #classified, clf, learning_curve = classify(train, test)
    plt = plot_learning_curve(
        estimator=MultinomialNB(),
        title="Test Learning Curve",
        X=data[["a", "b", "c", "d"]],
        y=data["label"],
        ylim=None,
        cv=None,
        n_jobs=1,
        train_sizes=np.linspace(.1, 1.0, 5)
    )
    plt.show()
    #classified, params, best_parameters = classify(train, test)
    #print(classified)
    #print(best_parameters["clf"])

if __name__ == "__main__":
    main()
