#!/usr/bin/env python

import sys
from os import path
import re
import os
from collections import namedtuple
from contextlib import nested


OFFSETS_SUFF = '.offset'
POSTAGGED_SUFF = '.tps'
CLEARNLP_POSTAGGED_SUFF = '.txt.pos'

import logging
logging.basicConfig()
LOG = logging.getLogger()
LOG.setLevel(logging.WARN)

REPLACEMENTS = {
    '-LRB-': '(',
    '-RRB-': ')',
    '-LSB-': '[',
    '-RSB-': ']',
}

def read_postags_and_offsets(pos_tagged_file, offsets_file):
    all_offsets = list(read_offsets(offsets_file))
    all_word_pos = list(read_word_pos(pos_tagged_file))
    for offsets, word_postags in zip(all_offsets, all_word_pos):
        if len(offsets) != len(word_postags):
            raise OffsetMismatchException("Offset mismatch for %s" % (offsets_file.name))
        LOG.debug("POS tags are: %r", word_postags)
        LOG.debug("Offsets are: %r", offsets)
        pos_nodes = []
        for offset, word_postag in zip(offsets, word_postags):
            wordform, postag = word_postag
            pos_nodes.append(POSNode(wordform, postag, offset))
        yield pos_nodes


def read_offsets(infile):
    for line in infile:
        yield [int(num) for num in line.rstrip().split(' ')]


def read_word_pos(infile):
    for line in infile:
        word_pos_tags = list(word_pos_tags_from_line(line))
        LOG.debug("Line '%s' gives word/POS tags %r", line, word_pos_tags)
        yield word_pos_tags


def word_pos_tags_from_line(line):
    for word_pos in line.rstrip().split(' '):
        word, pos = word_pos.rsplit('/', 1)
        word = REPLACEMENTS.get(word, word) # unescape eg -LRB-
        yield (word, pos)


def convert_from_sd_postagged_dirs_std(parse_root, output_dir):
    pos_tagged_dir = path.join(parse_root, 'postagged')
    offsets_dir = path.join(parse_root, 'offsets')
    convert_from_sd_postagged_dirs(pos_tagged_dir, offsets_dir, output_dir)


def convert_postags_in_file_to_clearnlp(pos_tagged_file, 
        offsets_file, output_file):
    pos_nodes = read_postags_and_offsets(
            pos_tagged_file, offsets_file)
    for pn_list in pos_nodes:
        for pn in pn_list:
            output_file.write(pn.in_cnlp_format())
        output_file.write('\n')


def convert_from_sd_postagged_dirs(pos_tagged_dir, offsets_dir, output_dir):
    for pos_basename in os.listdir(pos_tagged_dir):
        if not pos_basename.endswith(POSTAGGED_SUFF):
            continue
        stem = pos_basename[:-len(POSTAGGED_SUFF)]
        pos = path.join(pos_tagged_dir, pos_basename)
        offs = path.join(offsets_dir, stem + OFFSETS_SUFF)
        if not path.exists(offs):
            LOG.error("No offset file %s; not converting", offs)
            continue
        cnlp = path.join(output_dir, stem + CLEARNLP_POSTAGGED_SUFF)
        with nested(open(pos), open(offs), open(cnlp, 'w')) as (
                pos_file, offs_file, cnlp_file):
            convert_postags_in_file_to_clearnlp(pos_file, offs_file, cnlp_file)


class POSNode(object):
    def __init__(self, form, pos, start):
        self.form = form
        self.pos = pos
        self.start = start
    
    @property
    def end(self):
        return self.start + len(self.form)
    
    def in_cnlp_format(self):
        return "{0.form}\t{0.pos}\t{0.start:d}\t{0.end:d}\n".format(self)


class OffsetMismatchException(Exception):
    pass


def main():
    convert_from_sd_postagged_dirs_std(*sys.argv[1:])


if __name__ == "__main__":
    main()
        