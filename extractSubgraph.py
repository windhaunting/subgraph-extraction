#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 14:20:09 2017

@author: fubao
"""

import sys
import csv
import os
from collections import defaultdict
from random import sample
from random import choice

sys.path.append("../")

from hierarchicalQueryPython.CommonFiles.commons  import mycsv_reader
from hierarchicalQueryPython.CommonFiles.commons  import writeListRowToFileWriterTsv
from hierarchicalQueryPython.CommonFiles.commons  import  appendStringRowToFileWriterTsv


from hierarchicalQueryPython.graphCommon import readCiscoDataGraph
from hierarchicalQueryPython.graphCommon import readEdgeListToGraph
from hierarchicalQueryPython.graphCommon import PRODUCTDATATYPE

from hierarchicalQueryPython.graphCommon import SYNTHETICGRAPHNODETYPE


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
#extract ratio of subgraph from data graph

class ClsSubgraphExtraction(object):

    def __init__(self):
      pass
    
    def funcExtractSubGraph(self, G, startNodeSet, endNodeSet, specNodeNum, queryNodeNum, dstTypeLst):
        '''
        extract query graph for experiments.
        query graph size definition: specific node number-spn,  unknown query nodes- qn;      (spn, qn)
        startNodeSet indicates the set with the node type of query node starting; endNodeSet indicates the node type of query node ending
        '''
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
        
        #print ("divideSpecNodeNum, : ", divideSpecNodeNum)
        
        queryGraphLst = []            # every element is a list [(nodeId, nodeId type)...]
        dstTypeIndex = 0              #which query node type
        for src in startNodeSet:
            #breakFlag = False
            for dst in endNodeSet:
                print(" xxxx ", src, dst)
                if src != dst:
                    #get all path
                    #print(" xxxx dddddd", src, dst)
                    #print ("nx.all_simple_paths: ")
                    #print (" ", list(nx.all_simple_paths(G, src, dst, cutoff= 100)))
                    #timeBegin = time.time()
                    
                    for path in nx.all_simple_paths(G, src, dst, cutoff= 11):
                        #check how many product inside the path
                        #check how many has product type in the path
                        #print(" path aaaaa", len(path))
                        prodNodes = []
                        tmpTargetIndex = 0
                        for nodeId in path:
                            if G.node[nodeId]['labelType'] == dstTypeLst[tmpTargetIndex]:
                                #print ("xxxxxxx: ", node)
                                prodNodes.append(nodeId)
                                tmpTargetIndex += 1
                                if len(prodNodes) >= queryNodeNum:
                                    break
                        if len(prodNodes) >= queryNodeNum:
                           # breakFlag = True
                            #get the 
                            #print(" resNodesPath ", path)
                            #cntQueryNum = 0
                            prevj = 0
                            for nd in path:
                                innerLst = []
                                #print(" len dstTypeLst ", len(dstTypeLst), dstTypeIndex, specNodeNum, queryNodeNum)
                                dstType = dstTypeLst[dstTypeIndex]               #get query node type
                                if G.node[nd]['labelType'] == dstType:
                                    #get node neighbor for specific number
                                    nbs = G[nd]  
                                    tmpCnt = 0
                                    j = prevj
                                    nbsLst= list(nbs.keys())
                                    #print ("type: ", type(nbs), len(nbsLst))
                                    while (j < len(nbsLst)):
                                        nb = nbsLst[j]
                                        if G.node[nb]['labelType'] != dstType and (nb, G.node[nb]['labelType']) not in innerLst:
                                            innerLst.append((nb, G.node[nb]['labelType']))
                                            tmpCnt += 1
                                            if innerLst in queryGraphLst:
                                                innerLst.pop()
                                            elif innerLst not in queryGraphLst and tmpCnt >= divideSpecNodeNum[dstTypeIndex]:  #safisfy specific number
                                                #cntQueryNum += 1
                                                queryGraphLst.append(innerLst)
                                                #print(" dstTypeIndex aa ", dstTypeIndex)
                                                dstTypeIndex += 1    #change next dstType index 
                                                if dstTypeIndex >= queryNodeNum:
                                                    #print(" queryGraphLst ", queryGraphLst)
                                                    return path, queryGraphLst
                                                break
                                        j += 1
                                    prevj = j
                                            
    
                                    
    def funcExecuteExtractQueryProduct(self, G, outFile):
        '''
        extract product data query graph  entry    
        '''
        #nodeLst = G.nodes()
        #print ("node number: ", len(nodeLst), G.node[1]['labelType'])
        
        productNodeSet = set()
        #vulnerNodeSet = set()
        for n, d in G.nodes_iter(data=True):
            if d['labelType'] == 0:
                productNodeSet.add(n)
            #if d['labelType'] == 1:
            #    vulnerNodeSet.add(n)
    
        print ("productNodeSet: ", len(productNodeSet))
        #workgroup = ((u,v) for u,v,d in G.nodes_iter(data=True) if d['labelType']==5)
        
        
       # specNodeNum = 13
       # queryNodeNum = 10
        
        specNodesQueryNodesLst = [(2, 1),(4, 2), (6,3)]    # [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
        
        os.remove(outFile) if os.path.exists(outFile) else None
        
        fd = open(outFile,'a')
        for tpls in specNodesQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            dstTypeLst = [0]*queryNodeNum
    
            path, queryGraphLst = self.funcExtractSubGraph(G, productNodeSet, productNodeSet, specNodeNum, queryNodeNum, dstTypeLst)
    
            writeLst = []              #format: x,x;x,x;    x,x;,x,x....
            for specNumLst in queryGraphLst:
                inputStr = ""
                for tpl in specNumLst[:-1]:
                    inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                    
                inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])
                writeLst.append(inputStr)  
                
            writeListRowToFileWriterTsv(fd, writeLst, '\t')
    
    
    def funcExecuteExtractQueryDblp(self, dblpNodeInfoFile, edgeListFile, outFile):
        '''
        extract dblp data query graph entry
        '''
        G = readEdgeListToGraph(edgeListFile, dblpNodeInfoFile)
        peopleNodeSet = set()
        for n, d in G.nodes_iter(data=True):
            if d['labelType'] == 1:
                peopleNodeSet.add(n)
        print ("peopleNodeSet: ", len(peopleNodeSet))
         
        specNodesQueryNodesLst = [(2, 1),(4, 2), (6,3)]   #        [(2, 1),(4, 2), (4,3), (5,4), (6,5), (7,6), (8, 8), (10,10)]
        os.remove(outFile) if os.path.exists(outFile) else None
    
        fd = open(outFile,'a')
        for tpls in specNodesQueryNodesLst:
            specNodeNum = tpls[0]
            queryNodeNum = tpls[1]
            dstTypeLst = [1]*queryNodeNum
    
            path, queryGraphLst = self.funcExtractSubGraph(G, peopleNodeSet, peopleNodeSet, specNodeNum, queryNodeNum, dstTypeLst)
            
            writeLst = []              #format: x,x;x,x;    x,x;,x,x....
            for specNumLst in queryGraphLst:
                inputStr = ""
                for tpl in specNumLst[:-1]:
                    inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
                    
                inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])
                writeLst.append(inputStr)  
                
            writeListRowToFileWriterTsv(fd, writeLst, '\t')   
            


    def subgraphFromDatagraph(self, G, rationofNodes, prevNodeSet):
        '''
        get subgraph from datagraph,  get 10% of data; 10%, 20%, 50, 80%, 100% 
        accumulate rationode, including previous node set
        '''
        #get random number of nodes
        numberIncreaseNodes = int(len(G)*rationofNodes) - len(prevNodeSet)
        print ("G numberNodes: ", len(prevNodeSet) + numberIncreaseNodes)
        
        leftNodes = set(G.nodes()) - set(prevNodeSet)
        numberNodesLst = prevNodeSet + sample(leftNodes, numberIncreaseNodes)
        #get subgraph
        subGraph = G.subgraph(numberNodesLst)    
        return subGraph, numberNodesLst


    
    def executeSubgraphExtractFromDatagraph(self, G, outputDir):
        '''
        #extract subgraph from data graph
        '''
        #10%, 20%, 50%, 80%, 100
      
        print ("G: ", len(G))
        rationofNodesLst= [0.1, 0.2, 0.5, 0.8, 1.0]
        prevNodeSet = []
        for rationofNodes in rationofNodesLst: 
            subG, numberNodesLst = self.subgraphFromDatagraph(G, rationofNodes, prevNodeSet)
            prevNodeSet = numberNodesLst
            #write out file
            directoryPath = outputDir + "dataGraphInfo" + str(rationofNodes)
            if not os.path.exists(directoryPath):
                os.makedirs(directoryPath)
            outFileEdgeLst =  directoryPath + "/edgeListPart" + str(rationofNodes)
            outFileNodeInfo = directoryPath + "/nodeInfoPart" + str(rationofNodes)
            os.remove(outFileEdgeLst) if os.path.exists(outFileEdgeLst) else None
            os.remove(outFileNodeInfo) if os.path.exists(outFileNodeInfo) else None

            #fh=open(outFile,'wb')
            #nx.write_edgelist(G, fh)
            #os.remove(outFileEdgeLst) if os.path.exists(outFileEdgeLst) else None
            
            fdEdge = open(outFileEdgeLst,'a')
            fdInfo = open(outFileNodeInfo,'a')
            nodeInfoLstCheckMap = {}
            for edge in subG.edges_iter(data='edgeHierDistance', default=1):
                #print ("edge: ", edge)
                nodeId1 = int(edge[0])
                node1LabelType = G.node[nodeId1]['labelType']       #G[nolabelType(0)
                node1LabelName = G.node[nodeId1]['labelName']  
                
                nodeInfoLst1 = [node1LabelName + "+++" + str(node1LabelType), nodeId1]
                
                if nodeId1 not in nodeInfoLstCheckMap:
                    writeListRowToFileWriterTsv(fdInfo, nodeInfoLst1, '\t')
                    nodeInfoLstCheckMap[nodeId1] = 1
                    
                nodeId2 = int(edge[1])
                node2LabelType = G.node[nodeId2]['labelType']       #G[nolabelType(0)
                node2LabelName = G.node[nodeId2]['labelName']
                nodeInfoLst2 = [node2LabelName + "+++" + str(node2LabelType), nodeId2]
                if nodeId2 not in nodeInfoLstCheckMap:
                    writeListRowToFileWriterTsv(fdInfo, nodeInfoLst2, '\t')
                    nodeInfoLstCheckMap[nodeId2] = 1

                if edge[2] == 0:
                    edgeStr = "same"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')
                elif edge[2] == 1:
                    edgeStr = "higher"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')
                elif edge[2] == -1:
                    edgeStr = "lower"
                    writeListRowToFileWriterTsv(fdEdge, [edge[0], edge[1], edgeStr], '\t')                    
            fdEdge.close()
            fdInfo.close()



                                        
def getTypeNodeSet(G, nodeType):
    '''
    get nodes with a specific node type
    '''
    nodeSet = set()
    for n, d in G.nodes_iter(data=True):
        if d['labelType'] == nodeType:
            nodeSet.add(n)
                 
    return nodeSet


def funcMainStarQueryExatractDblpProduct():
    '''
    #extract subgraph as star query here from dblp data graph
    '''
     totalExpectedExtractedHierarchicalNodes = 4             #how many specific nodes expected to extract
    totalHierarchicalNodesTypeLst = [PRODUCTDATATYPE.VULNERABILITY.value, PRODUCTDATATYPE.TECHNOLOGY.value]
    
    totalNonHierarchicalNodes = 0
    
    
def funcMainStarQueryExatractCiscoProduct():
    '''
    extract star query graph from cisco data graph;   specific nodes number
    '''
    
    totalExpectedExtractedHierarchicalNodes = 4             #how many specific nodes expected to extract
    totalHierarchicalNodesTypeLst = [PRODUCTDATATYPE.VULNERABILITY.value, PRODUCTDATATYPE.TECHNOLOGY.value]
    
    totalNonHierarchicalNodes = 0
    nonHierarchicalNodeTypesLst = [PRODUCTDATATYPE.BUGID.value, PRODUCTDATATYPE.WORKAROUND.value, PRODUCTDATATYPE.WORKGROUP.value, PRODUCTDATATYPE.PRODUCTSITE.value]
    hopsVisited = 2
    hierarchicalLevelType = PRODUCTDATATYPE.PRODUCT.value

    ciscoNodeInfoFile = "../inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "../inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    
    G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    
    subFunctionStarQueryExtract(G, hierarchicalLevelType, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited)
      
    
#extract subgraph as star query here from synthetic data graph
def funcMainStarQueryExatractSyntheticGraph():
    '''
    extract star query graph from synthetic data graph;   specific nodes number
    '''
    totalExpectedExtractedHierarchicalNodes = 10             #how many specific nodes expected to extract
    totalHierarchicalNodesTypeLst = [SYNTHETICGRAPHNODETYPE.TYPE0INHERIT.value, SYNTHETICGRAPHNODETYPE.TYPE1INHERIT.value]
    
    totalNonHierarchicalNodes = 0
    nonHierarchicalNodeTypesLst = [SYNTHETICGRAPHNODETYPE.TYPE0GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE1GENERIC.value, SYNTHETICGRAPHNODETYPE.TYPE2GENERIC.value]
    hopsVisited = 1
    hierarchicalLevelType = SYNTHETICGRAPHNODETYPE.TYPE0HIER.value
    
    syntheticGraphEdgeListFile = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphEdgeListInfo.tsv"
    syntheticGraphNodeInfo = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraph_hierarchiRandom/syntheticGraphNodeInfo.tsv"
    G = readEdgeListToGraph(syntheticGraphEdgeListFile, syntheticGraphNodeInfo)
    
    subFunctionStarQueryExtract(G, hierarchicalLevelType, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited)


def subFunctionStarQueryExtract(G, hierarchicalLevelType, totalExpectedExtractedHierarchicalNodes, totalHierarchicalNodesTypeLst, nonHierarchicalNodeTypesLst, totalNonHierarchicalNodes, hopsVisited):
    '''
    1)specific node number in total
    2)hierarchical inheritance node number in total
    3)non-hierarchical inheritance node number in total
    4)hops of hierarchical node from query node to specific node
    '''
    
    #get nodes with hierarchical levels; e.g. product type
    hierNodeSet = getTypeNodeSet(G, hierarchicalLevelType)
    print ("funcMainStarQueryExatract: , G len ", len(G), hierarchicalLevelType, len(hierNodeSet))
    
    answerNodes = []
    
    i = 0
    #random visit a node
    flagCurrentNode = True
    resNodeQueryLst = []
    while (i < len(hierNodeSet)):
        #random get node
        node = choice(list(hierNodeSet))
        hierNodeSet.remove(node)
        
        #print ("funcMainStarQueryExatract node:  ", node)
        #find non-hierarchical inherited nodes first
        #check node neighbor
        for nb in G[node]:
            if G.node[nb]['labelType'] in nonHierarchicalNodeTypesLst:
                if len(resNodeQueryLst) >= totalNonHierarchicalNodes:
                    break
                resNodeQueryLst.append(nb)

        if len(resNodeQueryLst) < totalNonHierarchicalNodes:         #no neighbor nodes of node satifying requirement                     
            flagCurrentNode = True
        if not flagCurrentNode:
            flagCurrentNode = True
            continue                 #continue 
        else:
            # continue to search the hierarchical inheritance nodes; search the neighbor nodes again.
            #nodesLst = single_source_shortest_path(G, node, hopsVisited)          #time complexity is high
            answerNodes = getFixedHopsNodes(G, node, hierarchicalLevelType, totalHierarchicalNodesTypeLst[0] , hopsVisited)
            if len(set(answerNodes)) > totalExpectedExtractedHierarchicalNodes:           #find all the answers
                resNodeQueryLst += list(set(answerNodes))
                break
        i += 1
        
    resSpecificNodesLst = []                      #final result list (specific node, nodeType)
    for nodeId in resNodeQueryLst:
         resSpecificNodesLst.append((nodeId, G.node[nodeId]['labelType']))
         
    print ("funcMainStarQueryExatract specific query nodes: ", resSpecificNodesLst)
    return resSpecificNodesLst



def getFixedHopsNodes(G, sourceNode, nodeIntermedType, nodeLastType, hopsVisited):
    '''
    get the path from sourceNode with fixed hops and has the nodeType for all the nodes in the path; 
    use BFS search
    '''
    answerNodes = []
    queue = [(sourceNode, 0)] #nodeId, level 0 
    explored = defaultdict()
    while queue:
        #pop
        nodeInfo = queue.pop(0)
        nodeId = nodeInfo[0]
        nodeLevel = nodeInfo[1]
        if nodeLevel == hopsVisited and nodeLastType== G.node[nodeId]['labelType']:          #get the answer node
            explored[nodeId] = True              #level arrived
            answerNodes.append(nodeId)
        elif nodeLevel > hopsVisited:
            #print ("getFixedHopsNodes node level: ", len(answerNodes), nodeLevel)
            break
        
        if G.node[nodeId]['labelType'] != nodeIntermedType:
            explored[nodeId] = True          #mark as explored
            
        if nodeId not in explored:
            # add node to list of checked nodes
            explored[nodeId] = True
            nbs = G[nodeId]   #get neighbors
            for neighbour in nbs:
                queue.append((neighbour, nodeLevel+1))
 
    return answerNodes


def funcMainEntryExecuteExtract():
    '''
    main function extract subgraph as generic query graph
    '''
    ciscoNodeInfoFile = "../inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "../inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    
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
    
    outFile = "../hierarchicalQueryPython/output/extractSubgraphOutput/ciscoDataExtractQueryGraph"
    os.remove(outFile) if os.path.exists(outFile) else None

    fd = open(outFile,'a')
    
    for tpls in specNodesQueryNodesLst:
        specNodeNum = tpls[0]
        queryNodeNum = tpls[1]
        path, queryGraphLst = extractSubGraph(G, productNodeSet, specNodeNum, queryNodeNum)

        writeLst = []              #format: x,x;x,x;    x,x;,x,x....
        for specNumLst in queryGraphLst:
            inputStr = ""
            for tpl in specNumLst[:-1]:
            
                inputStr += str(tpl[0]) + "," + str(tpl[1]) + ";"
            inputStr += str(specNumLst[-1][0]) + "," + str(specNumLst[-1][1])
            writeLst.append(inputStr)  
            
        writeListRowToFileWriterTsv(fd, writeLst, '\t')
    

def subgraphForQueryExecute():
    '''
    query graph subtraction
    '''
    subgraphExtractionObj = ClsSubgraphExtraction()
    ciscoNodeInfoFile = "../../../hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "../../../hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    outFile = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/extractSubgraphQueryOutput/ciscoDataExtractQueryGraph01"
    #G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    #subgraphExtractionObj.funcExecuteExtractQueryProduct(G, outFile)             #extract query graph from data graph
    
    dblpNodeInfoFile = "../dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
    edgeListFile = "../dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
    outFile = "output/extractDblpQuerySizeGraph/dblpDataExtractQueryGraph.tsv"
    #subgraphExtractionObj.funcExecuteExtractQueryDblp(dblpNodeInfoFile, edgeListFile, outFile)
    
    
    
def subgraphExtractRatiosExecute():
    '''
    data graph subtraction for dblp data
    '''
    inputEdgeListFile = "../dblpParserGraph/output/finalOutput/newOutEdgeListFile.tsv"
    inputDblpNodeInfoFile = "../dblpParserGraph/output/finalOutput/newOutNodeNameToIdFile.tsv"
    outputDir = "output/dblpDataGraphExtractOut/"       #output directory
    #G = readdblpDataGraph(inputEdgeListFile, inputDblpNodeInfoFile)
    #subgraphExtractionObj.executeSubgraphExtractFromDatagraph(G, outputDir)
    
    
    #query graph subtraction from data subgraph
    inputDblpNodeInfo01File = "output/dblpDataGraphExtractOut/dataGraphInfo0.1/nodeInfoPart0.1"   
    inputEdgeList01File = "output/dblpDataGraphExtractOut/dataGraphInfo0.1/edgeListPart0.1"   
    outFile = "output/extractDblpQuerySizeGraph/subDatagraphExtract/dblpData01ExtractQueryGraph.tsv"
    subgraphExtractionObj.funcExecuteExtractQueryDblp(inputDblpNodeInfo01File, inputEdgeList01File, outFile)             #extract query graph from data graph
    
    
    #data graph subtraction for cisco data
    ciscoNodeInfoFile = "../../../hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "../../../hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"

    # G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    # outputDir = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/ciscoProductDataGraphExtractOut/"
    # subgraphExtractionObj.executeSubgraphExtractFromDatagraph(G, outputDir)
        

    #query graph extraction from cisco data graph ( all ratios of data graph)
    inputProductNodeInfo01File = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/ciscoProductDataGraphExtractOut/dataGraphInfo0.1/nodeInfoPart0.1"   
    inputProductEdgeList01File = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/ciscoProductDataGraphExtractOut/dataGraphInfo0.1/edgeListPart0.1"   
    outFile = "../../../hierarchicalNetworkQuery/hierarchicalQueryPython/output/extractSubgraphQueryOutput/subDatagraphExtract/ciscoProductsData01ExtractQueryGraph.tsv"
    #G = readdblpDataGraph(inputProductEdgeList01File, inputProductNodeInfo01File)       #here use readdblpdatagraph, because it's edge list file, not adjcency list file

   # subgraphExtractionObj.funcExecuteExtractQueryProduct(G, outFile)             #extract query graph from data graph
    

        
#main 
def main():
    #subgraphForQueryExecute()
    #subgraphExtractRatiosExecute()
    
    funcMainStarQueryExatractCiscoProduct()            
    #funcMainStarQueryExatractSyntheticGraph()
    
if __name__== "__main__":
  main()
  
