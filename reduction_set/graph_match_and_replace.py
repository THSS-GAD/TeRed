#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : lxx
# @time    : 2023/11/28 16:45
# @function: implement subgraph matching and replacement.
# @version : V1


import json
import os

import shutil
import networkx as nx

def match_and_replace(origin_graph_data, template_subgraph):
    # 返回完成替换后的图数据
    origin_graph = nx.Graph()
    label_data = {}
    node_list = []
    edge_list = []
  

    with open(origin_graph_data) as f:
        graph_data = json.load(f)
    nodes = graph_data['nodes']
    edges = graph_data['links']
    for d in nodes:
        idx = 0
        if 'id' in d:
            idx = d['id']
            del d['id']
        node_list.append((idx,d))
    for e in edges:
        source = e['source']
        target = e['target']  
        del e['source'],e['target'],e['ts'],e['success'],e['source_type']
        edge_list.append((source,target,e))
    origin_graph.add_nodes_from(node_list)
    origin_graph.add_edges_from(edge_list)


    template_graph = nx.Graph()
    label_data = {}
    node_list = []
    edge_list = []
    with open(template_subgraph) as f:
        graph_data = json.load(f)
    nodes = graph_data['nodes']
    edges = graph_data['links']
    for d in nodes:
        idx = 0
        if 'id' in d:
            idx = d['id']
            del d['id']
        # print(d)
        node_list.append((idx,d))
    # print(node_list)
    for e in edges:
        source = e['source']
        target = e['target']  
        del e['source'],e['target']
        edge_list.append((source,target,e))
    template_graph.add_nodes_from(node_list)
    template_graph.add_edges_from(edge_list)


    GM = nx.isomorphism.GraphMatcher(origin_graph,template_graph)
    # GM = nx.algorithms.isomorphism.GraphMatcher(G,G2,edge_match=nx.isomorphism.categorical_edge_match(['syscall'],['read']))
    # GM = nx.algorithms.isomorphism.GraphMatcher(origin_graph,template_graph,node_match=nx.isomorphism.categorical_node_match(['type'],['file']))
    # GM = nx.algorithms.isomorphism.GraphMatcher(G,G2,node_match=nx.isomorphism.categorical_node_match(['type'],['file']),edge_match=nx.isomorphism.categorical_edge_match(['syscall'],['read']))
    flag_subgraph_is_isomorphic = GM.subgraph_is_isomorphic()
    print(flag_subgraph_is_isomorphic)
    mapping = GM.mapping 

    with open(origin_graph_data) as f:
        graph_data = json.load(f)
    nodes = graph_data['nodes']
    edges = graph_data['links']
    newnodes = []
    keylists=mapping.keys()
    print(keylists)
    for d in nodes:
        if not d['id'] in mapping:
            newnodes.append(d)
          
    compressed_id = 'Compressed_wget_'+template_subgraph
    if flag_subgraph_is_isomorphic:
        print(compressed_id)
        newnodes.append({'id':compressed_id,'pid':"1"})
    
    new_edges = []
    for e in edges:
        source = e['source']
        target = e['target']  
        if source in keylists and target in keylists:
            continue
        elif source in keylists :
            e['source'] = compressed_id
            new_edges.append(e)
        elif target in keylists :
            e['target'] = compressed_id
            new_edges.append(e)
        else:
            new_edges.append(e)
    graph_dict = {}
    graph_dict['nodes'] = newnodes
    graph_dict['links'] = new_edges
    compressed_output_file = origin_graph_data
    with open(compressed_output_file,"w") as f:
        json.dump(graph_dict,f)
    pass
