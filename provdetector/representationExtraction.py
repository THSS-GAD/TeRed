import math
from Graph import *


def extraction(G, T):
    H = {}
    OUT = []
    IN = []
    Host_Num = 0

    for i in range(len(G)):
        Host_Num += 1
        H_now = {}
        OUT_now = {}
        IN_now = {}
        for j in G[i].e_type:
            if not j in H.keys():
                H[j] = 1
                H_now[j] = 1
            elif not j in H_now.keys():
                H_now[j] = 1
                H[j] += 1
        for j in range(len(G[i].e_src)):
            if G[i].e_src[j] == G[i].node_cnt - 2 or G[i].e_dst[j] == G[i].node_cnt - 1: continue
            if not G[i].e_src[j] in OUT_now.keys():
                OUT_now[G[i].e_src[j]] = []
            if not G[i].e_dst[j] in IN_now.keys():
                IN_now[G[i].e_dst[j]] = []
            if not int(G[i].e_ts[j] / T) in OUT_now[G[i].e_src[j]]:
                OUT_now[G[i].e_src[j]].append(int(G[i].e_ts[j] / T))
            if not int(G[i].e_ts[j] / T) in IN_now[G[i].e_dst[j]]:
                IN_now[G[i].e_dst[j]].append(int(G[i].e_ts[j] / T))
        OUT_now_final = {}
        IN_now_final = {}
        T_total = int((G[i].max_ts - G[i].min_ts) / T) + 1
        for j in range(len(G[i].e_src)):
            if G[i].e_src[j] == G[i].node_cnt - 2 or G[i].e_dst[j] == G[i].node_cnt - 1: continue
            OUT_now_final[G[i].e_src[j]] = float(len(OUT_now[G[i].e_src[j]]) / T_total)
            IN_now_final[G[i].e_dst[j]] = float(len(IN_now[G[i].e_dst[j]]) / T_total)
        OUT.append(OUT_now_final)
        IN.append(IN_now_final)

    for i in range(len(G)):
        for j in range(len(G[i].e_src)):
            if G[i].e_src[j] == G[i].node_cnt - 2 or G[i].e_dst[j] == G[i].node_cnt - 1:
                temp = -1
                G[i].W.append(temp)
                continue
            temp = float(H[G[i].e_type[j]] / len(G))
            temp *= OUT[i][G[i].e_src[j]]
            temp *= IN[i][G[i].e_dst[j]]
            temp = -math.log(temp)
            temp *= -1  # 取负值，从而使得后续求最短路径的算法实际上求的是最长路径
            G[i].W.append(temp)


def work(_G, k):
    # SPFA算法求每个节点到End node的最短路径
    spfa_list = []
    dist_list = []
    route_list = []
    spfa_list.append(_G.node_cnt - 1)
    for i in range(_G.node_cnt - 1):
        dist_list.append(1)
        route_list.append([])

    dist_list.append(0)
    route_list.append([])

    while len(spfa_list) > 0:
        node_now = spfa_list.pop(0)
        for i in _G.in_edges[node_now]:
            if dist_list[node_now] + _G.W[i] < dist_list[_G.e_src[i]]:
                dist_list[_G.e_src[i]] = dist_list[node_now] + _G.W[i]
                route_list[_G.e_src[i]] = []
                for ii in route_list[node_now]:
                    route_list[_G.e_src[i]].append(ii)
                route_list[_G.e_src[i]].append(i)
                if not _G.e_src[i] in spfa_list:
                    spfa_list.append(_G.e_src[i])

    # Eppstein算法求前K条最短路径
    for i in range(_G.node_cnt):
        route_list[i].reverse()

    side_track = []
    for i in range(_G.edge_cnt):
        side_track.append(dist_list[_G.e_dst[i]] + _G.W[i] - dist_list[_G.e_src[i]])

    ans_route = []
    ans_route.append(route_list[_G.node_cnt - 2])
    path_flag = []
    for i in range(_G.edge_cnt):
        if i in route_list[_G.node_cnt - 2]:
            path_flag.append(1)
        else:
            path_flag.append(0)

    for i in range(k - 1):
        min_len = -1
        min_path = []
        for route_now in ans_route:
            pre_route = []
            for j in route_now:
                for next_path in _G.out_edges[_G.e_src[j]]:
                    if path_flag[next_path] == 1: continue
                    if min_len == -1:
                        min_len = side_track[next_path]
                        min_path = pre_route + [next_path] + route_list[_G.e_dst[next_path]]
                pre_route.append(j)
        ans_route.append(min_path)
        for j in min_path:
            path_flag[j] = 1

    doc_ans = []
    for i in ans_route:
        temp = ''
        for k in range(len(i)):
            j = i[k]
            if k == 0 or k == len(i)-1: continue
            if _G.nodeType_map[_G.e_src[j]] == 'process':
                temp += _G.nodeType_map[_G.e_src[j]] + ' ' + _G.nodeName_map[_G.e_src[j]].split('|')[0] + ' '
            else:
                temp += _G.nodeType_map[_G.e_src[j]] + ' ' +  _G.nodeName_map[_G.e_src[j]] + ' '
            temp += _G.e_type[j] + ' '
            if k == len(i) - 2:
                if _G.nodeType_map[_G.e_dst[j]] == 'process':
                    temp += _G.nodeType_map[_G.e_dst[j]] + ' ' +  _G.nodeName_map[_G.e_dst[j]].split('|')[0]
                else:
                    temp += _G.nodeType_map[_G.e_dst[j]] + ' ' +  _G.nodeName_map[_G.e_dst[j]]
        doc_ans.append(temp)
    return doc_ans
