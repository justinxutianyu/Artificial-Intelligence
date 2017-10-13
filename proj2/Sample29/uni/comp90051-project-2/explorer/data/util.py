import os

from glob import glob

###################
# Utility Classes #
###################

class Crawler(object):
    """
    Implements a crawler for identifying files of
    a certain type.
    """

    def __init__(self):
        self.type = "*"

    def set_type(self, file_type):
        self.type = file_type

    def crawl(self, directory):
        return [filename
                for path in os.walk(directory)
                for filename in glob(os.path.join(path[0], '*.' + self.type))]

#####################
# Utility Functions #
#####################

def splitFileName(filename):
    """
    Takes a file and returns a double of the
    form:

    (filename, extension)

    Example:
    Input  - "foo.txt"
    Output - "foo", ".txt"
    """
    return os.path.splitext(filename)

def splitPath(filename):
    """
    Takes a file and returns a double of the
    form:

    (absolute_path_to_file, filename)

    Windows example:
    Input  - "foo.txt"
    Output - "C:\\users\\name\\", "foo.txt"
    """
    return os.path.split(os.path.abspath(filename))

def tokenize(string, stopwords=[]):
    """
    Tokenizes a string. During tokenization
    punctuation is removed and case-folding is
    performed. This can be disabled by commenting
    lines 1 and 2 respectively.

    Tokenization relies on a naive means of
    splitting text using the split() method.
    This is done mostly for performance reasons.

    Input:
    string    - text.
    stopwords - optional list of stopwords to exclude
                from token list.

    Output:
    Generator of tokens from text.
    """
    string = string.translate(None, punctuation)
    string = string.lower()
    return (
        token for token in string.split()
        if token not in stopwords
    )
