import csv
import json
import os
import networkx as nx
import collections
import shutil
import random
import pathlib
from tqdm import tqdm
from processData import parse
from preprocess import preprocess
from train import model_train
from predict import model_predict
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

def processTestNormalFile(files,source_dir):
    normal_cnt=0
    normal_file = []
    for file in files:
        if "normal" in file:
            normal_cnt+=1
            normal_file.append(file)
         # 计算需要重命名的文件数量
    num_files_to_rename = int(normal_cnt * 0.3)
    # 随机选择需要重命名的文件
    files_to_rename = random.sample(normal_file, num_files_to_rename)
    
    # 重命名文件
    for file in files_to_rename:
        old_path = os.path.join(source_dir, file)
        new_path = os.path.join(source_dir, f"test_{file}")
        os.rename(old_path, new_path)
        print(f"Renamed '{file}' to 'test_{file}'")
def processData(source_dir,target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    print(target_dir)
    files = os.listdir(source_dir)
    processTestNormalFile(files,source_dir)
    files = os.listdir(source_dir)
    # 将获取的所有文件名进行循环判断
    for file in files:
        print(file)
        if "attack" in file:
            parse(source_dir,file,target_dir+"/attack.log")
        if "test" in file:
            parse(source_dir,file,target_dir+"/normal_test.log")
        elif "normal" in file:
            parse(source_dir,file,target_dir+"/normal.log")

def copyFile(source_dir,target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for filename in os.listdir(source_dir):
        # 源文件的绝对路径
        source_file = os.path.join(source_dir, filename)
        # 如果是文件
        if os.path.isfile(source_file):
            # 把文件复制到目标文件夹
            shutil.copy(source_file, target_dir)

source_folder = '../reduced_output/darpa_to_json'
target_dir="output/"
processData(source_folder,target_dir)
class_num = preprocess(target_dir)
model_train(class_num,target_dir)
model_predict(0.5,target_dir)
print("done ")