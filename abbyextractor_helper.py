# coding: utf-8
import os
import unicodedata
import string
import regex

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),'home/ahmed/internship/ocr_cnn/data/interim/brut'))

def write(filename, data, supplier=None):
    if supplier is not None:
        path = '{}/{}--{}.tf'.format(OUT_DIR, supplier.rstrip().lower(), filename)
    else :
        path = '{}/{}.tf'.format(OUT_DIR, filename)

    out_file = open(path, 'w')

    for word_features in data:
        out_file.write(word_features.get_representation())
    out_file.close()

def flatten(data: list):
    words_list = list()
    for block in data:
        for line in block:
            words_list.extend(line.copy())

    words_list = list(filter(lambda x: len(x.word) > 0, words_list))
    return words_list

def normalize(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()
    return regex.sub('\s+', s, ' ').replace(' ', '')