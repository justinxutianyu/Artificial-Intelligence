#!/usr/bin/python
'''
Variome Train Test Split Script

Splits Variome into training and testing data sets.

Author: Kai Hirsinger (kai.hirsinger@gmail.com)
Since:  29th May 2016
'''

###########
# Imports #
###########

import argparse
import itertools
import os
import pandas as pd
import random
import shutil

#################################
# Command Line Argument Parsing #
#################################

parser = argparse.ArgumentParser()
parser.add_argument(
    '-s', '--size',
    type=int,
    required=True,
    help='Size of the training data set, as a percentage.'
)
parser.add_argument(
    '-d', '--directory',
    type=str,
    required=True,
    help='Location of the Variome annotated documents'
)
args = parser.parse_args()

#############
# Constants #
#############

VARIOME_DIRECTORY = args.directory

TRAIN_SIZE = args.size
TEST_SIZE  = 100 - args.size

#Number of representations a relation must have to be
#considered as a candidate for producing a train/test split
REPRESENTATION_THRESHOLD = 100

###########
# Classes #
###########

class AnnotationFile(object):

    def __init__(self, filename):
        self.filename  = filename
        self.text_file = os.path.splitext(filename)[0] + '.txt'

        #Read the relations and themes from the file
        with open(filename) as relation_file:
            relations, themes = dict(), dict()
            for line in relation_file:
                if line[0] == 'T':
                    theme = Theme()
                    theme.from_theme_annotation(line)
                    themes[theme.id] = theme
                elif line[0] == 'R':
                    relation = Relation()
                    relation.from_relation_annotation(line)
                    relations[relation.id] = relation

        #Construct the full types of each relation
        #This is done as a post-processing step because we require the themes
        for relation_id, relation in relations.items():
            relation.construct_full_type(themes)

        self.themes = themes
        self.relations = relations

    def count_relations(self):
        counts = dict()
        for relation in self.relations.values():
            try:
                counts[relation.full_type] += 1
            except KeyError:
                counts[relation.full_type] = 1
        return counts

class Relation(object):

    def __init__(self):
        self.id        = str()
        self.base_type = str()
        self.full_type = str()
        self.args      = tuple()

    def from_relation_annotation(self, line):
        relation_id, text   = line.split('\t')
        relation_components = text.split()
        relation_type, args = relation_components[0], relation_components[1:]
        relation_args       = [arg.split(':') for arg in args]
        self.id        = relation_id
        self.base_type = relation_type.lower()
        self.args      = tuple([arg[1] for arg in relation_args])

    def construct_full_type(self, theme_map):
        args = sorted([
            theme_map[self.args[0]].type,
            theme_map[self.args[1]].type
        ])
        self.full_type = '{}{}{}'.format(
            args[0].replace('-', '').replace('_', ''),
            self.base_type,
            args[1].replace('-', '').replace('_', '')
        )

class Theme(object):

    def __init__(self):
        self.id   = str()
        self.type = str()

    def from_theme_annotation(self, line):
        theme_id, text = line.split('\t')[:2]
        theme_type     = text.split()[0].lower()
        self.id   = theme_id
        self.type = theme_type

####################
# Helper Functions #
####################

def get_absolute_file_path(filename):
    return os.path.normpath(
        os.path.join(
            VARIOME_DIRECTORY, filename
        )
    )

def get_annotation_files(directory):
    return [
        file_name for file_name in
        os.listdir(directory)
        if os.path.splitext(file_name)[1] == '.ann'
    ]

def get_relation_distribution(annotation_files):
    counts = dict()
    for annotation_file in annotation_files:
        for relation,count in annotation_file.count_relations().items():
            try:
                counts[relation]['total_occurrences'] += count
                counts[relation]['doc_appearances'] += 1
                if count < counts[relation]['min_occurences']:
                    counts[relation]['min_occurences'] = count
                if count > counts[relation]['max_occurences']:
                    counts[relation]['max_occurences'] = count
            except KeyError:
                counts[relation] = {
                    'total_occurrences': count,
                    'doc_appearances': 1,
                    'min_occurences': count,
                    'max_occurences': count
                }
    for relation in counts:
        counts[relation]['mean_occurrences'] = \
            float(counts[relation]['total_occurrences']) / float(counts[relation]['doc_appearances'])
    return counts

def subset_sum_to_s(key_value_set, n, s, c):
    '''
    Gets all subsets of int_set of size n
    that sum to between s - c and s + c.

    Note that c represents an error term,
    allowing for approximate subsets to
    be drawn from int_set.
    '''
    subsets = itertools.combinations(key_value_set, n)

    for subset in subsets:
        subset_sum = 0
        processed  = 0
        is_good = True
        for elem in subset:
            subset_sum += elem[1]
            processed  += 1
            if (subset_sum >= (s - c)) and (subset_sum <= (s + c)):
                is_good = False
                break
        if is_good or (processed == len(subset)):
            yield subset
        else:
            continue
    yield None

def percent_split(total, perecent):
    train = int(total * (float(TRAIN_SIZE) / 100.0))
    test  = total - train
    return train, test

def copy_fileset(fileset, destination):
    for file in fileset:
        shutil.copy(
            file.filename,
            os.path.join(destination, os.path.split(file.filename)[1])
        )
        shutil.copy(
            file.text_file,
            os.path.join(destination, os.path.split(file.text_file)[1])
        )

def create_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

#################
# Main Function #
#################

def main():
    annotation_files = [
        AnnotationFile(get_absolute_file_path(filename))
        for filename in get_annotation_files(VARIOME_DIRECTORY)
    ]
    relation_counts = get_relation_distribution(annotation_files)
    for relation,counts in relation_counts.items():
        counts['relation'] = relation

    #Dump the counts to file, for analysis
    #pd.DataFrame(relation_counts.values()).to_csv(
    #    '{}/relation_stats.csv'.format(VARIOME_DIRECTORY)
    #)
    with open('{}/variome_stats.txt'.format(VARIOME_DIRECTORY), 'w') as stats_file:
        stats_file.write("""
\\begin{table*}[t]
\\begin{tabular}{ | l | l | l | l | }
\hline
\multicolumn{4}{ | c | }{Variome Corpus Relation Distribution} \\\\
\hline
Relation Type & Total Appearances & Proportion of Documents Present (\%) \\\\
\hline
        """)
        stats_file.writelines([
            "{0} & {1} & {2:.2f} \\\\\n".format(
                record['relation'],
                record['total_occurrences'],
                (float(record['doc_appearances']) / 120.0) * 100
            )
            for record in relation_counts.values()
        ])
        stats_file.write("""
\\hline
\\end{tabular}
\\caption{
	Variome corpus relation distribution.
}
\\label{table:results}
\\end{table*}
        """)
    file_train_size, file_test_size = percent_split(
        len(annotation_files),
        TRAIN_SIZE
    )
    print("Proposed Train Size: {}".format(file_train_size))
    print("Proposed Test Size: {}".format(file_test_size))
    print('')

    #Build up a dictionary mapping relation_type -> a
    #set of (AnnotatedFile, int) doubles, where the int
    #is the count of the relation_type in that file.
    relation_filecounts = dict()
    for relation,count in relation_counts.items():
        if count['total_occurrences'] >= REPRESENTATION_THRESHOLD:
            file_counts = set()
            for ann_file in annotation_files:
                counts = ann_file.count_relations()
                try:
                    file_counts.add( (ann_file, counts[relation]) )
                except KeyError:
                    file_counts.add( (ann_file, 0) )
            relation_filecounts[relation] = file_counts

    for relation in relation_filecounts:
        print("Doing relation {}".format(relation))
        train_directory = get_absolute_file_path('{}/train'.format(relation))
        test_directory  = get_absolute_file_path('{}/test'.format(relation))
        create_directory(train_directory)
        create_directory(test_directory)

        relation_train_size, relation_test_size = percent_split(
            relation_counts[relation]['total_occurrences'],
            TRAIN_SIZE
        )
        #Build up  the test set, then get the training set by taking the
        #complement over the original annotated file set
        test_set = relation_filecounts[relation]
        subsets  = subset_sum_to_s(
            test_set,
            file_test_size,
            relation_test_size,
            0
        )
        test_set  = set([pair[0] for pair in subsets.next()])
        train_set = set(annotation_files) - test_set

        copy_fileset(test_set, test_directory)
        copy_fileset(train_set, train_directory)

        print("Resulting Train Size: {}".format(len(train_set)))
        print("Resulting Test Size: {}".format(len(test_set)))

        test_files = [
            AnnotationFile(get_absolute_file_path(filename))
            for filename in get_annotation_files(test_directory)
        ]
        print("Identified {} test files".format(len(test_files)))
        test_counts = get_relation_distribution(test_files)
        for _relation,counts in test_counts.items():
            counts['relation'] = _relation

        train_files = [
            AnnotationFile(get_absolute_file_path(filename))
            for filename in get_annotation_files(train_directory)
        ]
        print("Identified {} train files".format(len(train_files)))
        train_counts = get_relation_distribution(train_files)
        for _relation,counts in train_counts.items():
            counts['relation'] = _relation

        train_count = train_counts[relation]['total_occurrences']
        test_count  = test_counts[relation]['total_occurrences']
        train_pct   = float(train_count) / float(train_count + test_count) * 100
        test_pct    = float(test_count) / float(train_count + test_count) * 100
        print("Training data occurrences: {} ~ {}%".format(
            train_count,
            round(train_pct, 2)
        ))
        print("Test data occurrences: {} ~ {}%".format(
            test_count,
            round(test_pct, 2)
        ))

        with open(get_absolute_file_path('{}/stats.txt'.format(relation)), 'w') as relation_stats_file:
            relation_stats_file.write(
"""
Training Data
-------------
Size (Files): {1}
Total relations of type "{0}": {2} ({3:.2f}%)

Test Data
-------------
Size (Files): {4}
Total relations of type "{0}": {5} ({6:.2f}%)
""".format(relation, len(train_files), train_count, train_pct, len(test_files), test_count, test_pct)
            )


if __name__ == '__main__':
    main()
