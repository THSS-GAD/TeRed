import numpy as np
from Graph import *


def graphBuilding(path_list):
    G = []
    for i in path_list:
        f_now = open(i, 'r', encoding='utf-8')
        G_now = Graph()
        cnt = 0
        line_now = []
        ts_now = []
        for line in f_now:
            line_now.append(line)
            ts_now.append(float(line.strip('\n').split('\t')[5]))
        sorted_index = np.argsort(ts_now, axis=0)
        line_now = np.array(line_now)[sorted_index]

        for line in line_now:  # srcId srcType dstId dstType edgeType timestamp
            line = line.strip('\n').split('\t')
            temp = float(line[5])
            if G_now.min_ts < 0: G_now.min_ts = temp
            if G_now.max_ts < 0: G_now.max_ts = temp
            if temp < G_now.min_ts: G_now.min_ts = temp
            if temp > G_now.max_ts: G_now.max_ts = temp

            if not line[0] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[0]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[0]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[0]] = 1
                G_now.node_cnt += 1
            if not line[2] in G_now.nodeId_map.keys():
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1
            if G_now.flag[line[2]] == 1:
                G_now.nodeId_map[line[2]] = G_now.node_cnt
                G_now.nodeName_map[G_now.node_cnt] = line[2]
                G_now.out_edges[G_now.node_cnt] = []
                G_now.in_edges[G_now.node_cnt] = []
                G_now.flag[line[2]] = 0
                G_now.node_cnt += 1

            G_now.flag[line[0]] = 1  # 修改，避免环路问题

            G_now.nodeType_map[G_now.nodeId_map[line[0]]] = line[1]
            G_now.nodeType_map[G_now.nodeId_map[line[2]]] = line[3]
            G_now.out_edges[G_now.nodeId_map[line[0]]].append(G_now.edge_cnt)
            G_now.in_edges[G_now.nodeId_map[line[2]]].append(G_now.edge_cnt)
            G_now.e_src.append(G_now.nodeId_map[line[0]])
            G_now.e_dst.append(G_now.nodeId_map[line[2]])
            G_now.e_type.append(line[4])
            G_now.e_ts.append(float(line[5]))
            G_now.edge_cnt += 1

        G_now.nodeType_map[G_now.node_cnt] = 'start'
        G_now.nodeId_map['Start_node'] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = 'Start_node'
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        G_now.nodeType_map[G_now.node_cnt] = 'end'
        G_now.nodeId_map['End_node'] = G_now.node_cnt
        G_now.nodeName_map[G_now.node_cnt] = 'End_node'
        G_now.out_edges[G_now.node_cnt] = []
        G_now.in_edges[G_now.node_cnt] = []
        G_now.node_cnt += 1
        for j in range(G_now.node_cnt - 2):
            if len(G_now.in_edges[j]) == 0:
                G_now.out_edges[G_now.node_cnt - 2].append(G_now.edge_cnt)
                G_now.in_edges[j].append(G_now.edge_cnt)
                G_now.e_src.append(G_now.node_cnt - 2)
                G_now.e_dst.append(j)
                G_now.e_type.append('start_edge')
                G_now.e_ts.append(max(G_now.min_ts - 100, 0))
                G_now.edge_cnt += 1

            if len(G_now.out_edges[j]) == 0:
                G_now.out_edges[j].append(G_now.edge_cnt)
                G_now.in_edges[G_now.node_cnt - 1].append(G_now.edge_cnt)
                G_now.e_src.append(j)
                G_now.e_dst.append(G_now.node_cnt - 1)
                G_now.e_type.append('end_edge')
                G_now.e_ts.append(G_now.min_ts + 100)
                G_now.edge_cnt += 1

        G.append(G_now)
    return G
