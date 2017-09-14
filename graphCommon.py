# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 14:48:29 2017

@author: fubao
"""
import codecs
import csv
import collections
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph;
import json
import webbrowser

#from preprocessCiscoData import  readCiscoNodesInfo

#read Graph

'''
def readGraph(adjacentListFile, nodeInfoFile1, nodeInfoFile2):
    
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')
    
    NodeNameMap = {}         #including previousDrugDBNodeMap ; #NewExerciseNodeMap
    
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 4:
                nodeId = row[0].strip().lower()         #string type
                nodeName = row[3].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                    
    with codecs.open(nodeInfoFile2, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 4:
                nodeId = row[0].strip().lower()         #string type
                nodeName = row[3].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName                

    G = nx.Graph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].split(';')[0].strip().lower())
                neighborLst = row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, type = nodeType, name=nodeName)
                for nb in neighborLst:
                    G.add_edge(nodeId, int(nb))
                
    print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    print('G edges: ', G.edges())
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()            
    nx.draw(G, with_labels = True)        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('labels.png')
    return G   
'''

def readTestGraph(adjacentListFile):
    G = nx.Graph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].split(';')[0].strip().lower())
                neighborLst = row[1].split(';')[1].strip().lower().split(' ')
                
                G.add_node(nodeId, labelType = nodeType)
                for nb in neighborLst:
                    G.add_edge(nodeId, int(nb))
                
    print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    print('G edges: ', G.edges())
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()            
    nx.draw(G, with_labels = True)        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('labels.png')
    return G   
    
#read animal graph, multi edge graph
#sameHierarchy, higherHierarchy, lowerHierarchy edge

#node type:  0: animal
#            1: property
def readAnimalGraph(adjacentListFile, nodeInfoFile1):
    #G.add_node('abc', dob=1185, pob='usa', dayob='monday')
    
    NodeNameMap = {}
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                                        
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].strip().lower())      # int(row[1].split(';')[0].strip().lower())
                neighborEdgeStr= row[2].strip().lower()        # row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, labelType=nodeType, labelName=nodeName)
                
                #hierarchy are recorded in the edge property
                sameIndex = neighborEdgeStr.find('same::')
                
                if sameIndex != -1:
                    #print ('xxx: ', len(lst), neighborEdgeStr[sameIndex+6:].split(' '))
                    for nb1 in neighborEdgeStr[sameIndex+6::].split(' '):
                        if 'lower::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            #print ('nb1: ', nb1)
#                            if nb1 == '54692':
#                                print ('nb1: ', nb1)
                            nb = nb1.strip().lower()
                            G.add_edge(nodeId, int(nb), key='sameHierarchy', edgeHierDistance = 0)
                
                higherIndex = neighborEdgeStr.find('higher::')
                if higherIndex != -1:
                    for nb1 in neighborEdgeStr[higherIndex+8::].split(' '):
                        if 'lower::' in nb1 or 'same::' in nb1:
                            break
                        else:
                            #print ('nb: ', nb1, nodeId)
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='higherHierarchy', edgeHierDistance = 1)
                
                lowerIndex = neighborEdgeStr.find('lower::')
                if lowerIndex != -1:
                    for nb1 in neighborEdgeStr[lowerIndex+7::].split(' '):
                        if 'same::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='lowerHierarchy', edgeHierDistance = -1)
                
#                if i >= 1:
#                    break
#                i += 1
                
    #print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['type'], nx.get_node_attributes(G,'type')[1])
    #print('G edges: ', G.edges())
    #print ('G one node: ', G[1], len(G[1]))    
    #print ('G one node2: ', G[54692], len(G[54692]))            
    #print ('G one edge18: ', G[1][8])    #['relativeHierarchy']['edgeHierDistance'] 
    #print ('G one edge2: ', G[2][54355]['relativeHierarchy']['edgeHierDistance'])
    #print ('G one edge3: ', G[54355][2])    
    #print ('G one edge4: ', G[54355][2]['relativeHierarchy']['edgeHierDistance'])
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()  
    #nodes = [i for i in range(1, 3)]
    #subG = G.subgraph(nodes) 
    #nx.draw(subG, with_labels = True, labels =nx.get_node_attributes(subG,'labelName'))  
    #nx.draw(G, with_labels = True, labels =nx.get_node_attributes(G,'labelName'))        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('graph.pdf')

    return G 

'''
0	product
1	vulnerability
2	bug_Id
3	workaround
4	technology
5	workgroup
6	product site
'''

# read cisco product data graph
def readCiscoDataGraph(adjacentListFile, ciscoNodeInfoFile):

    NodeNameMap = {}
    with codecs.open(ciscoNodeInfoFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                if nodeId not in NodeNameMap:
                    NodeNameMap[nodeId] = nodeName
                    
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(adjacentListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                nodeId = int(row[0])
                nodeType = int(row[1].strip().lower())      # int(row[1].split(';')[0].strip().lower())
                neighborEdgeStr= row[2].strip().lower()        # row[1].split(';')[1].strip().lower().split(' ')
                
                if nodeId in NodeNameMap:
                    nodeName = NodeNameMap[nodeId]
                else:
                    nodeName = "test"
                G.add_node(nodeId, labelType=nodeType, labelName=nodeName)
                
                #hierarchy are recorded in the edge property
                sameIndex = neighborEdgeStr.find('same::')
                
                if sameIndex != -1:
                    #print ('xxx: ', len(lst), neighborEdgeStr[sameIndex+6:].split(' '))
                    for nb1 in neighborEdgeStr[sameIndex+6::].split(' '):
                        if 'lower::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            #print ('nb1: ', nb1)
#                            if nb1 == '54692':
#                                print ('nb1: ', nb1)
                            #print ('nodeIdaa: ',nodeId)
                            nb = nb1.strip().lower()
                            if nb != '':
                                G.add_edge(nodeId, int(nb), key='sameHierarchy', edgeHierDistance = 0)
                
                higherIndex = neighborEdgeStr.find('higher::')
                if higherIndex != -1:
                    for nb1 in neighborEdgeStr[higherIndex+8::].split(' '):
                        if 'lower::' in nb1 or 'same::' in nb1:
                            break
                        else:
                            #print ('nb: ', nb1, nodeId)
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='higherHierarchy', edgeHierDistance = 1)
                
                lowerIndex = neighborEdgeStr.find('lower::')
                if lowerIndex != -1:
                    for nb1 in neighborEdgeStr[lowerIndex+7::].split(' '):
                        if 'same::' in nb1 or 'higher::' in nb1:
                            break
                        else:
                            nb = nb1.strip().lower()
#                            if nb == '54692':
#                                print ('nb1: ', nb)
                            G.add_edge(nodeId, int(nb), key='lowerHierarchy', edgeHierDistance = -1)
                
#                if i >= 1:
#                    break
#                i += 1
                
    #print('G nodes: ', G.nodes(), "ddddd= ")  # G.node[1]['labelType'], nx.get_node_attributes(G,'labelType')[1])
    #print('G edges: ', G.edges())
    #print ('G one node: ', G[1], len(G[1]))    
    #print ('G one node2: ', G[54692], len(G[54692]))            
    #print ('G one edge18: ', G[1][8])    #['relativeHierarchy']['edgeHierDistance'] 
    #print ('G one edge2: ', G[2][54355]['relativeHierarchy']['edgeHierDistance'])
    #print ('G one edge3: ', G[54355][2])    
    #print ('G one edge4: ', G[54355][2]['relativeHierarchy']['edgeHierDistance'])
    #nx.draw(G, pos=nx.spring_layout(G))
    #nx.draw_networkx_labels(G,pos=nx.spring_layout(G))
    #plt.show()  
    #nodes = [i for i in range(1, 3)]
    #subG = G.subgraph(nodes) 
    #nx.draw(subG, with_labels = True, labels =nx.get_node_attributes(subG,'labelName'))  
    #nx.draw(G, with_labels = True, labels =nx.get_node_attributes(G,'labelName'))        # labels=nx.get_node_attributes(G,'type'))
    #plt.savefig('graph.pdf')
    return G


#read dblp data graph

def readdblpDataGraph(edgeListFile, dblpNodeInfoFile):

    nodeIdtoNameMap = {}             #nodeId to node name
    nodeIdtoTypeMap = {}             #nodeId to node type 
    with codecs.open(dblpNodeInfoFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 2:
                #print ("nodeType:", row)
                nodeId = int(row[1].strip().lower())         #string type
                nodeName = row[0].split("+++")[0].strip().lower()
                nodeType = int(row[0].split("+++")[1].strip().lower())
                if nodeId not in nodeIdtoNameMap:
                    nodeIdtoNameMap[nodeId] = nodeName
                    nodeIdtoTypeMap[nodeId] = nodeType
        
    G = nx.MultiDiGraph()           #nx.DiGraph() 
    with codecs.open(edgeListFile, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        #i = 0
        for row in tsvin:
            if len(row) >= 3:
                nodeSrcId = int(row[0].strip())                      #src node Id
                nodeDstId = int(row[1].strip())                     #dst node Id
                edgeStr =  row[2].strip().lower()
                #get node type
                nodeSrcType = nodeIdtoTypeMap[nodeSrcId]
                nodeDstType = nodeIdtoTypeMap[nodeDstId]
                nodeSrcName = nodeIdtoNameMap[nodeSrcId]
                nodeDstName = nodeIdtoNameMap[nodeDstId]
                G.add_node(nodeSrcId, labelType=nodeSrcType, labelName=nodeSrcName)
                G.add_node(nodeDstId, labelType=nodeDstType, labelName=nodeDstName)
                
                #update src
                if edgeStr == "same":
                    G.add_edge(nodeSrcId, nodeDstId, key='higherHierarchy', edgeHierDistance = 0)
                elif edgeStr == "higher":
                    G.add_edge(nodeSrcId, nodeDstId, key='higherHierarchy', edgeHierDistance = 1)
                elif edgeStr == "lower":
                    G.add_edge(nodeSrcId, nodeDstId, key='higherHierarchy', edgeHierDistance = -1)


    #print ('G one node: ', G[1], len(G[1]))    
    return G

                    
#basic statisics of the graph
def statistGraphInfo(G):
    nodeNum = len(G)
    edgeNum = G.size()
    
    avgDegree = sum(G.degree().values())/float(len(G))
    print ('graphInfo: ', nodeNum, edgeNum, avgDegree)
    
#read the string to id;  natural language processing tranformation;
def queryInputStringtoNodeId(nodeInfoFile1, inputNameLst):
    nodeNameMap = {}
    nodeIdTypeMap = {}
    nodeIdTypeNameMap = {}
    #labelSet = set()
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                nodeTypeId = int(row[2].strip().lower())
                nodeTypeName = row[3].strip().lower()
                if nodeName not in nodeNameMap:
                    nodeNameMap[nodeName] = nodeId
                if nodeId not in nodeIdTypeMap:
                    nodeIdTypeMap[nodeId] = nodeTypeId
                if nodeId not in nodeIdTypeNameMap:
                    nodeIdTypeNameMap[nodeId] = nodeTypeName
                    #if nodeTypeId != 0:    #all properties type
                #    labelSet.add(nodeTypeName)
                
    #labelLst = list(labelSet)
    inputSrcNodeIdLst = []
    inputNameLst = [name.lower().strip() for name in inputNameLst]
    for ls in inputNameLst:
        inputSrcNodeIdLst.append(nodeNameMap[ls])
        #print ('input name id: ',ls, nodeNameMap[ls])
    return inputSrcNodeIdLst, nodeIdTypeMap, nodeIdTypeNameMap




'''
def queryInputStringtoNodeIdNew(nodeInfoFile1):
    nodeNameMap = {}
    nodeIdTypeMap = {}
    nodeIdTypeNameMap = {}
    nodeTypeNametoIdMap = {}
    #labelSet = set()
    with codecs.open(nodeInfoFile1, 'rU') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t', quoting=0)
        for row in tsvin:
            if len(row) >= 3:
                nodeId = int(row[0].strip().lower())         #string type
                nodeName = row[1].strip().lower()
                nodeTypeId = int(row[2].strip().lower())
                nodeTypeName = row[3].strip().lower()
                if nodeName not in nodeNameMap:
                    nodeNameMap[nodeName] = nodeId
                if nodeId not in nodeIdTypeMap:
                    nodeIdTypeMap[nodeId] = nodeTypeId
                if nodeId not in nodeIdTypeNameMap:
                    nodeIdTypeNameMap[nodeId] = nodeTypeName
                    #if nodeTypeId != 0:    #all properties type
                #    labelSet.add(nodeTypeName)
                if nodeTypeName not in nodeTypeNametoIdMap:
                    nodeTypeNametoIdMap[nodeTypeName] = nodeTypeId
                    
                
    #labelLst = list(labelSet)

    return nodeIdTypeMap, nodeIdTypeNameMap, nodeTypeNametoIdMap
'''
 
def drawGraph(G, candidatesNodeIdLst):
    
    g = nx.Graph()           #nx.DiGraph() 
    edges = G.edges(candidatesNodeIdLst)
    print ('edges3: ', edges)
    for eg in edges:
        node0 = eg[0]
        node1 = eg[1]
        g.add_node(node0, labelName = G.node[node0]['labelName'])
        g.add_node(node1, labelName = G.node[node1]['labelName'])
        g.add_edge(eg[0], eg[1])
    pos = nx.spring_layout(g)
    #A = [3]
    #noCor = ["b" if n in A else "r" for n in G.nodes()]
    nx.draw(g, pos=pos, with_labels = True, labels =nx.get_node_attributes(g,'labelName'))   # labels =nx.get_node_attributes(G,'labelName'))
    #nx.draw_networkx_edges(G,pos=pos, edgelist = edges, node_color='b')
    #h = G.subgraph(A)
    #nx.draw_networkx_nodes(h,pos=pos, node_color=noCor) #or even nx.draw(h,pos=pos,node_color='b') to get nodes and edges in one command
    #nx.draw_networkx_edges(h,pos=pos)
    plt.savefig('graph.pdf')

def drawDegree(G):
    #G = nx.gnp_random_graph(100, 0.02)
    #average degree
    
    averDegree = sum(G.degree().values())/len(G.degree())
    print ('average degree: ', averDegree, G.number_of_edges())
    degree_sequence=sorted([d for n,d in G.degree().items()], reverse=True) # degree sequence
    #print ("Degree sequence", degree_sequence)
    degreeCount=collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())
    
    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')
    
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d+0.4 for d in deg])
    ax.set_xticklabels(deg)
    

#save to Json    
def saveToJson(G, fname):
    
    #json.dump(dict(nodes=[{"id": n, "group": G.node[n]['labelType']} for n in G.nodes()],
    #               links=[{"source":u, "target":v, "value":(G.node[u]['labelType'], G.node[v]['labelType'])} for u,v in G.edges()]),
    #          open(fname, 'w'), indent=2)
    
    json.dump(dict(links=[{"source":u, "target":v, "value":(G.node[u]['labelType'], G.node[v]['labelType'], 
                        G.node[u]['labelName'], G.node[v]['labelName'])} for u,v in G.edges()]),
              open(fname, 'w'), indent=2)
              
#    data = json_graph.node_link_data(G)
#    s = json.dumps(data)
#    f = open(fname, 'w')
#    f.write(s)
#    print ("s :  ", s)

def drawTestGraphOnline(G, outJsonFile):
    #test read
    adjacentListFile = "/home/fubao/Desktop/workDir/personalizedQuery/personalizedQuery_Drug/DataPrep/PersonalizedQueryPython/input/small_graph_adjacentList.txt"
    G = readTestGraph(adjacentListFile)
    saveToJson(G, outJsonFile)
    
def drawtopKRelatedGraph(G, allvisitedNodeForDraw, outJsonFile):
        #get nodes and edge to create a new graph
    newG = nx.MultiDiGraph()           #nx.DiGraph() 

    for nodeId in allvisitedNodeForDraw:
        nodeType = G.node[nodeId]['labelType']
        nodeName = G.node[nodeId]['labelName']
        newG.add_node(nodeId, labelType=nodeType, labelName=nodeName)
        neighbors = G.neighbors(nodeId)
        for nb in neighbors:
            #key = G[nodeId][nb]["key"]
            newG.add_edge(nodeId, nb)
            nodeType = G.node[nb]['labelType']
            nodeName = G.node[nb]['labelName']
            newG.add_node(nb, labelType=nodeType, labelName=nodeName)
    
    #print node and edge sizes
    print ('438 drawtopKRelatedGraph node and edge sizes: ', len(G), G.size(), len(newG), newG.size())
    saveToJson(newG, outJsonFile)
    webbrowser.get('firefox').open_new_tab('index2.html')  
    
#G = ""
#outJsonFile = "output/testOutput/test1.json"
#drawGraphOnline(G)
#drawtopKRelatedGraph(G,  outJsonFile)
#webbrowser.get('firefox').open_new_tab('index.html')    

def testFution():
    
    ciscoNodeInfoFile = "/home/fubao/workDir/ResearchProjects/hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphNodeInfo"
    ciscoAdjacentListFile = "/home/fubao/workDir/ResearchProjects/hierarchicalNetworkQuery/inputData/ciscoProductVulnerability/newCiscoGraphAdjacencyList"
    
    G = readCiscoDataGraph(ciscoAdjacentListFile, ciscoNodeInfoFile)
    statistGraphInfo(G)
    
#testFution()