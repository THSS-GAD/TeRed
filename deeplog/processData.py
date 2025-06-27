import csv
import json
import os
import networkx as nx
import collections
import shutil
import random
import pathlib
idx = 0
def get_filelist(dir, Filelist):
    files = os.listdir(dir)
    # 将获取的所有文件名进行循环判断
    for file in files:
  
        Filelist.append(file)
    return Filelist

def load_json_file(json_path):
    # print(json_path)
    try:
        json_file = open(json_path, 'r', encoding='gbk')
        file_dict = json.load(json_file)
    except:
        json_file = open(json_path, 'r', encoding='utf-8')
        file_dict = json.load(json_file)
 
    return file_dict

def parse(dir,input_file,output_file):
        graph_data = {}
        input_path = os.path.join(dir,input_file)
        # with open(input_path,'r',encoding='gbk') as f:
        graph_data = load_json_file(input_path)
        nodes = graph_data['nodes']
        edges = graph_data['links']
        log_format = '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>'
        name_to_node = {}
        for node in nodes:
            name_to_node[node['id']]=node
        global idx
        with open(output_file, 'a') as output:
            for edge in edges:
                edge["ts"] = edge["ts"][:-2]
                log_line = str(idx)+" "+"2017-05-14 "+edge["ts"]+" "+name_to_node[edge["source"]]["id"]+" INFO "+edge["source_type"]+" ["+edge["syscall"]+"] "+name_to_node[edge["target"]]["id"]+" "+edge["source_type"]+" "+edge["source"]+" "+edge["target"]+"\n"
                # print(log_line)
                # log_line = str(idx)+" "+"2017-05-14 "+edge["ts"]+" "+name_to_node[edge["source"]]["pid"]+" INFO "+edge["source_type"]+" ["+edge["syscall"]+"] "+edge["target_type"]+" "+edge["source_type"]+" "+edge["source"]+" "+edge["target"]+"\n"
                idx+=1
                output.write(log_line)


def get_all_second_level_folders(src_folder):
    second_level_folders = []
    
    # 遍历源文件夹的所有一级子文件夹
    for a_folder in os.listdir(src_folder):
        a_folder_path = os.path.join(src_folder, a_folder)
        if os.path.isdir(a_folder_path):
            # 遍历每个一级子文件夹下的所有二级子文件夹
            for b_folder in os.listdir(a_folder_path):
                b_folder_path = os.path.join(a_folder_path, b_folder)
                if os.path.isdir(b_folder_path):
                    # 添加二级子文件夹路径到列表
                    second_level_folders.append(b_folder_path)
    
    return second_level_folders

filelist = []

# data_dir ="darpa_to_json_theia"
# # 将源文件复制到目标文件夹中
# log_compress_dir = "../../Thss_DataReduction/test_data/"+data_dir+"_attack"
# target_dir = data_dir+"_uncompressed"
# copyAttackFromDataReductionToDeepLog(log_compress_dir,target_dir)
# log_compress_dir = "../../Thss_DataReduction/test_data/"+data_dir+"_normal"
# copyNormalFromDataReductionToDeepLog(log_compress_dir,target_dir)
# 定义源文件夹
# source_folder = '/example/reduced'
# # 获取所有二级子文件夹路径
# second_level_folders = get_all_second_level_folders(source_folder)
# for dir in second_level_folders
# files = os.listdir(dir)
    # 将获取的所有文件名进行循环判断

# for file in files:
#     print(file)
#     if "attack" in file:
#         parse(dir,file,dir+"_attack.log")
#     if "test" in file:
#         parse(dir,file,dir+"_normal_test.log")
#     else:
#         parse(dir,file,dir+"_normal.log")