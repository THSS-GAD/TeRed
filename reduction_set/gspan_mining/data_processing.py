import json
import os

import shutil

from settings import DATA_DIR

def read_json_file(processed_data,filename):
    graph_data = {}

    with open(filename) as f:
        graph_data = json.load(f)
    nodes = graph_data['nodes']
    for node in nodes:
        if 'id' not in node or 'type' not in node:
            print("Error: Node missing 'id' or 'type' field in file:", filename)
            continue
        writed_node = "v;"
        writed_node += node['id']+";"
        if node['type'] == 'process':
            # writed_node += node['pname']
            writed_node += node['pname']+"&"
            writed_node += node['type']

        elif node['type'] == 'file':
            #  writed_node += node['path']
            writed_node += node['path']+"&"
            writed_node += node['type']
        else: 
            writed_node += node['type']
        processed_data.write(writed_node)
        processed_data.write('\r\n')
    
    edges = graph_data['links']
    for edge in edges:
        writed_edge = "e;"
        writed_edge += edge['source']+";"
        writed_edge += edge['target']+";"
        writed_edge += edge['syscall']
        processed_data.write(writed_edge)
        processed_data.write('\r\n')

def process_json_files(graph_data):
    path = DATA_DIR + graph_data
    filelists = get_filelists_indir(path)
    print(filelists)
    cnt = 0
    if not os.path.exists('graphdata/'+graph_data):
        os.makedirs('graphdata/'+graph_data)
    # os.mkdir("output"+str(i))
    graph_data_file = 'graphdata/'+graph_data+'/graphdata.txt'
    if os.path.exists(graph_data_file):
        os.remove(graph_data_file)
    processed_data = open(graph_data_file, 'w+')
    idx = 0
    for file in filelists:
        processed_data.write("t;#;"+str(idx))
        processed_data.write('\r\n')
        idx+=1
        read_json_file(processed_data,file)
    processed_data.close()
    return graph_data_file

def get_filelist(dir, Filelist):
    newDir = dir
    # dirPath = glob.iglob('./CapitalMuseum/*')

    for s in os.listdir(dir):
	# 获取每个文件夹下的文件名并赋值给 file
        newDir=os.path.join(dir,s)
        files = os.listdir(newDir)
        test_list = []
    # 将获取的所有文件名进行循环判断
        for file in files:
            Dir_file=os.path.join(newDir,file)
            test_list.append(Dir_file)
        Filelist.append(test_list)
    return Filelist


def output_json_file(read_filename,output_json):
    read_file = open(read_filename, 'r')
    node_dict_lists = []
    edge_dict_lists = []
    node_dict = {}
    edge_dict = {}
    graph_dict = {}
    idx = 0
    max_graph_idx = 0
    max_ver_idx = 0
    tmp_graph_idx = 0
    for line in read_file.readlines():
        if line[0] == 't':
            tmp_graph_idx +=1
        if line[0] == 'v':
            ver = line.split()
            ver_idx = int(ver[1])
            if ver_idx>max_ver_idx:
                max_ver_idx =ver_idx
                max_graph_idx = tmp_graph_idx
    print(max_graph_idx,max_ver_idx)
    read_file = open(read_filename, 'r')
    for line in read_file.readlines():
        if line[0] == 't':
            idx +=1
        if idx > max_graph_idx:
            break
        if idx < max_graph_idx:
            continue
        if line[0] == 't':
            # idx +=1
            node_dict_lists = []
            edge_dict_lists = []
            node_dict = {}
            edge_dict = {}
            graph_dict = {}
        if line[0] == 'v':
            node_dict = {}
            ver = line.split()
            node_dict['id'] = ver[1]
            str_name = line[len(ver[0])+len(ver[1])+2:-1]
            if len(str_name.split('&')) == 1:
                node_dict['type'] = str_name.split('&')[0]
            else:
                node_dict['type'] = str_name.split('&')[1]
            if node_dict['type'] == 'process':
                node_dict['pname'] = str_name.split('&')[0]
            elif node_dict['type'] == 'file':
                node_dict['path'] = str_name.split('&')[0]
            node_dict_lists.append(node_dict)
        if line[0] == 'e':
            edge_dict = {}
            edge = line.split()
            edge_dict['source'] = edge[1]
            edge_dict['target'] = edge[2]
            edge_dict['syscall'] = edge[3]
            edge_dict_lists.append(edge_dict)
        if line[0] == 'S':
            graph_dict['nodes'] = node_dict_lists
            graph_dict['links'] = edge_dict_lists
            with open(output_json,"w") as f:
                json.dump(graph_dict,f)

def get_filelists_indir(path):

    files= os.listdir(path) #得到文件夹下的所有文件名称
    s = []
    for file in files: #遍历文件夹
        if not os.path.isdir(file): #判断是否是文件夹，不是文件夹才打开
            s.append(path+"/"+file) #每个文件的文本存到list中
    return s


    
