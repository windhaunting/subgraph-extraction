#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 14:20:09 2017

@author: fubao
"""


import codecs
import csv
import os
from collections import OrderedDict

from CommonFiles.commons import mycsv_reader
from CommonFiles.commons import writeListRowToFileWriterTsv
from CommonFiles.commons import  appendStringRowToFileWriterTsv

from graphCommon import readCiscoDataGraph

import networkx as nx
#extractSubGraph from data graph

from math import floor

'''
0	product
1	vulnerability
2	bug_Id
3	workaround
4	technology
5	workgroup
6	product site
'''

#extract query graph for experiments.
#query graph size definition: specific node number-spn,  unknown query nodes- qn;      (spn, qn)
def extractSubGraph(G, productNodeSet, specNodeNum, queryNodeNum, dstTypeLst):
    
    #find path of , 
    #get the specNodeNum
    divider = floor(specNodeNum/queryNodeNum)
    residual = specNodeNum % queryNodeNum
    
    divideSpecNodeNum = []
    for i in range(queryNodeNum):              #assign specNodeNum size for each queryNodeNum
        if residual != 0:
            divideSpecNodeNum.append(divider + 1)           
            residual -= 1
        else:
            divideSpecNodeNum.append(divider)
    
    print ("divideSpecNodeNum, : ", divideSpecNodeNum)
    
    queryGraphLst = []            # every element is a list [(nodeId, nodeId type)...]
    dstTypeIndex = 0              #which query node type
    
    for src in productNodeSet:
        #breakFlag = False
        for dst in productNodeSet:
            if src != dst:
                #get all path
                for path in nx.all_simple_paths(G, src, dst):
                    #check how many product inside the path
                    #check how many has product type in the path
                    prodNodes = []
                    for nodeId in path:
                        print(" queryNodeNum dstTypeId ", queryNodeNum, dstTypeIndex)
                        dstType = dstTypeLst[dstTypeIndex]
                        if G.node[nodeId]['labelType'] == 0:
                            #print ("xxxxxxx: ", node)
                            prodNodes.append(nodeId)
                        if len(prodNodes) >= queryNodeNum:
                           # breakFlag = True
                            #get the 
                            #print(" resNodesPath ", path)
                            cntQueryNum = 0
                            prevj = 0
                            for nd in path:
                                innerLst = []
                                if G.node[nd]['labelType'] == dstType:
                                    #get node neighbor for specific number
                                    nbs = G[nd]  
                                    tmpCnt = 0
                                    j = prevj
                                    #print ("type: ", type(nbs))
                                    nbsLst= list(nbs.keys())
                                    while (j < len(nbsLst)):
                                        nb = nbsLst[j]
                                        if G.node[nb]['labelType'] != dstType and (nb, G.node[nb]['labelType']) not in innerLst:
                                            innerLst.append((nb, G.node[nb]['labelType']))
                                            tmpCnt += 1
                                            if innerLst in queryGraphLst:
                                                innerLst.pop()
                                            elif innerLst not in queryGraphLst and tmpCnt >= divideSpecNodeNum[cntQueryNum]:  #safisfy specific number
                                                cntQueryNum += 1
                                                queryGraphLst.append(innerLst)
                                                dstTypeIndex += 1    #change next dstType index 
                                                print(" dstTypeIndex aa ", dstTypeIndex)
                                                if cntQueryNum >= queryNodeNum:
                                                    print(" queryGraphLst ", queryGraphLst)
                                                    return path, queryGraphLst
                                                break
                                        j += 1
                                    prevj = j
                                        

                                
                                

    
def executeExtractFunction():
    ciscoNodeInfoFile = "/home/fubao/workDir/ResearchProjects/hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "/home/fubao/workDir/ResearchProjects/hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    
    G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    
    #nodeLst = G.nodes()
    #print ("node number: ", len(nodeLst), G.node[1]['labelType'])
    
    productNodeSet = set()
    vulnerNodeSet = set()
    for n, d in G.nodes_iter(data=True):
        if d['labelType'] == 0:
            productNodeSet.add(n)
        if d['labelType'] == 1:
            vulnerNodeSet.add(n)

    print ("productNodeSet: ", len(productNodeSet))
    #workgroup = ((u,v) for u,v,d in G.nodes_iter(data=True) if d['labelType']==5)
    
    
   # specNodeNum = 13
   # queryNodeNum = 10
    
    specNodesQueryNodesLst = [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
    
    outFile = "/home/fubao/workDir/ResearchProjects/hierarchicalNetworkQuery/hierarchicalQueryPython/output/extractSubgraphOutput/ciscoDataExtractQueryGraph01"
    os.remove(outFile) if os.path.exists(outFile) else None

    fd = open(outFile,'a')
    
    for tpls in specNodesQueryNodesLst:
        specNodeNum = tpls[0]
        queryNodeNum = tpls[1]
        dstTypeLst = [0]*queryNodeNum

        path, queryGraphLst = extractSubGraph(G, productNodeSet, specNodeNum, queryNodeNum, dstTypeLst)


        writeLst = []              #format: x,x;x,x;    x,x;,x,x....
        for specNumLst in queryGraphLst:
            inputStr = ""
            for tpl in specNumLst[:-1]:
                inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                
            inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])
            writeLst.append(inputStr)  
            
        writeListRowToFileWriterTsv(fd, writeLst, '\t')
    
    
executeExtractFunction()