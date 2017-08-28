# coding: utf-8

import colorama
colorama.init(autoreset=True)
import os
import abbytraining as au
import pandas as pd
from word import WordFeature
#DATA_PARENT =  "/home/ahmed/Downloads/BOUYGUES_XML/"
DATA_DIR = "/home/ahmed/Downloads/BOUYGUES_XML/BOUYGUES_XML_0/"
#DATA_DIR = "/home/ahmed/Downloads/BOUYGUES_XML/BOUYGUES_XML_"
#CSV_DIR = "/home/ahmed/Downloads/BOUYGUES_CSV/"
#FILENAME = "BT0001030084"
FILENAME= "1841729699"
#FILENAME= "$*"
#FILENAME = "BT0001031148"
#FILENAME = "BT0001029649"
#FILENAME = "BT0001029733"

FILE = DATA_DIR + FILENAME + "_0001.xml.gz"
rootdir= "/home/ahmed/internship/cnn_ocr/BOUYGUES_XML/BOUYGUES_XML_0"
files= sorted(os.listdir(rootdir))
a = au.AbbyTraining(FILE)








'''
for file in files:
        #a= au.AbbyTraining(FILE)
        if file.endswith(".xml.gz"):
                a = au.AbbyTraining("/home/ahmed/internship/cnn_ocr/BOUYGUES_XML/BOUYGUES_XML_0/"+(file))
                #a.ens_brut_blcks[0]
                #a.ens_brut_blcks[1]
'''
#a = au.AbbyExtractor(FILE)
#a.get_words()
'''
rootdir="/home/ahmed/internship/cnn_ocr/BOUYGUES_XML/BOUYGUES_XML_0"
for files in os.walk(rootdir):
        #print(os.path.join(subdir,file))
        a = au.AbbyTraining(os.path.join(rootdir,files))
        a.ens_brut_blcks[0]
        a.ens_brut_blcks[1]
'''
