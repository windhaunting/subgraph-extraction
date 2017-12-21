#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 12:26:39 2017

@author: fubao
"""

from collections import defaultdict


def getTypeNodeSet(G, nodeType):
    '''
    get nodes with a specific node type
    '''
    nodeSet = set()
    for n, d in G.nodes_iter(data=True):
        if d['labelType'] == nodeType:
            nodeSet.add(n)
                 
    return nodeSet



def getFixedHopsNodes(G, sourceNode, nodeIntermedTypes, nodeLastType, hopsVisited):
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
        
        if G.node[nodeId]['labelType'] not in nodeIntermedTypes:
            explored[nodeId] = True          #mark as explored
            
        if nodeId not in explored:
            # add node to list of checked nodes
            explored[nodeId] = True
            nbs = G[nodeId]   #get neighbors
            for neighbour in nbs:
                queue.append((neighbour, nodeLevel+1))
 
    return answerNodes