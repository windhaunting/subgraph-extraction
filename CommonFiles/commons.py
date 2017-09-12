# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 11:52:41 2016

@author: fubao
"""

import csv
import os
import codecs

def mycsv_reader(csv_reader): 
  while True: 
    try: 
      yield next(csv_reader) 
    except csv.Error: 
      # error handling what you want.
      pass
    continue 
  return
  
def writeListRowToFileWriterTsv(fd, listRow, delimiter):
 #   with open(outFile, "a") as fd:
    writer = csv.writer(fd, delimiter = delimiter, lineterminator='\n')
    writer.writerows([listRow])

def appendStringRowToFileWriterTsv(fd, stringRow):
 #   with open(outFile, "a") as fd:
    #fd = open(outFile,'a')
    fd.write(stringRow)
    #fd.close()