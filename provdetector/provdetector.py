import os

import numpy as np

from representationExtraction import *
from graphBuilding import graphBuilding
from Graph import *
from embedding import *
from anomalyDetection import *
from parser import *
import time
import multiprocessing
from functools import partial


G = []


def set_para(_T, _K, _t):
    global T, K, THRESHOLD
    T = _T
    K = _K
    THRESHOLD = _t

set_para(150, 25, 2)


def detect(train_data: str, test_data: str):
    '''
    main scripts for provdetector
    Args:
        train_data (): train_graph path, should be like 'data/xxx'
        test_data (): test_graph path, should be like 'data/xxx'

    Returns:

    '''
    # 设置论文中的时间窗口大小参数T、异常路径top数K、以及一张图中有多少路径判定为异常就告警

    # 输入格式转换，将原有图格式转换为流式的6元组边格式，放入所在目录data文件夹下同名目录

    # train_dataset = 'data/ProvDetector/' + train_data.split('data/')[1]
    # test_dataset = 'data/ProvDetector/' + test_data.split('data/')[1]
    #
    # folder_json_to_tuple(train_data, train_dataset)
    # folder_json_to_tuple(test_data, test_dataset)

    train_file_name_list = os.listdir(train_data)
    train_path_list = [os.path.join(train_data, i) for i in train_file_name_list]
    test_file_name_list = os.listdir(test_data)
    test_path_list = [os.path.join(test_data, i) for i in test_file_name_list]

    # print(train_path_list + test_path_list)
    G = graphBuilding(train_path_list + test_path_list)  # 构建数据源图
    extraction(G, T)  # 提取所有图中边的表示数据

    # print(train_path_list)
    # print(test_path_list)

    doc_ans_train = []
    doc_ans_test = []
    for i in range(len(G)):
        if i >= len(train_path_list):
            break
        # print(f"working on train {i}: {train_path_list[i]}")
        doc_ans_train += work(G[i], K)  # 对于指定的图，计算路径异常指数并找到排名前K条边;训练时需要多张图的话，可以分别对每张图G[i]执行此操作，将结果合并到一个doc_ans中即可

    for i in range(len(G)):
        if i < len(train_path_list):
            continue
        # print(f"working on test {i}: {test_path_list[i - len(train_path_list)]}")
        doc_ans_test += work(G[i], K)
    # print('work complete')

    train_vec, vec_ans = embedding(doc_ans_train, doc_ans_test, K)  # 路径特征嵌入，得到测试集中提取的每条路径各自的特征

    # exit(0)

    # print("predict")
    predict_ans = LOF(train_vec, vec_ans, doc_ans_train, doc_ans_test)  # 使用离群点检测算法得到每条路径的异常预测

    os.makedirs('result', exist_ok=True)
    with open(f'result/train_{THRESHOLD}_{train_data.split("/")[0]}.txt', 'w') as f:
        for index, file_name in enumerate(train_file_name_list):
            doc = doc_ans_train[index * K: (index + 1) * K]
            for j in range(len(doc)):
                f.write(
                    f'{file_name}\t{str(doc[j])}\n')

    alert = []
    with open(f'result/alert_{THRESHOLD}_{test_data.split("/")[0]}.txt', 'w') as f:
        for index, file_name in enumerate(test_file_name_list):
            detection = predict_ans[index * K: (index + 1) * K]
            doc = doc_ans_test[index * K: (index + 1) * K]
            for j in range(len(detection)):
                f.write(
                    f'{file_name}\t{str(np.count_nonzero((detection == -1)))}\t{str(detection[j])}\t{str(doc[j])}\n')
            if np.count_nonzero((detection == -1)) > THRESHOLD:
                alert.append(file_name.split('.')[0])
    return(alert)


def provdector_test(train_data_list, test_data_list):
    count_ori_attack = 0
    count_attack = 0
    count_normal = 0
    count_all = 0
    for i in range(len(train_data_list)):
        train_data = train_data_list[i]
        test_data = test_data_list[i]
        test_result = detect(train_data, test_data)
        # 遍历文件名列表
        for filename in os.listdir(test_data):
            if "attack" in filename:
                count_ori_attack += 1
        for filename in test_result:
            count_all += 1
            # 判断文件名是否包含"attack"
            if "attack" in filename:
                count_attack += 1
            # 判断文件名是否包含"normal"
            elif "normal" in filename:
                count_normal += 1
    recall = count_attack / count_ori_attack
    precision = count_attack / count_all
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    print('precision:', precision, ' recall:', recall, ' f1_score:', f1_score)

def process_data(train_data, test_data, count_ori_attack, count_attack, count_all):
    test_result = detect(train_data, test_data)
    count_attack_local = 0
    count_normal_local = 0
    count_ori_attack_local = 0
    count_all_local = 0
    for filename in os.listdir(test_data):
        if "attack" in filename:
            count_ori_attack_local += 1
    for filename in test_result:
        count_all_local += 1
        if "attack" in filename:
            count_attack_local += 1

    with count_ori_attack.get_lock():
        count_ori_attack.value += count_ori_attack_local
    with count_attack.get_lock():
        count_attack.value += count_attack_local
    with count_all.get_lock():
        count_all.value += count_all_local

def provdector_test_multi(train_data_list, test_data_list):
    count_ori_attack = multiprocessing.Value('i', 0)
    count_attack = multiprocessing.Value('i', 0)
    count_all = multiprocessing.Value('i', 0)

    func = partial(process_data, count_ori_attack=count_ori_attack, count_attack=count_attack, count_all=count_all)

    processes = []
    for train_data, test_data in zip(train_data_list, test_data_list):
        p = multiprocessing.Process(target=func, args=(train_data, test_data))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    recall = count_attack.value / count_ori_attack.value
    precision = count_attack.value / count_all.value
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    print('precision:', precision, ' recall:', recall, ' f1_score:', f1_score)


def run_method_folder():
    method_list = ['Origin']
    # folder_list = ['cve-2014-6271-multi', 'cve-2016-4971_all', 'cve-2019-9193', 'theia', 'trace']
    folder_list = ['trace']


    for method in method_list:
        for folder in folder_list:
            train_data_list = []
            test_data_list = []
            for i in range(1, 6):
                train_data_list.append(f'data/test/folder_{i}/train_dataset')
                test_data_list.append(f'data/test/folder_{i}/test_dataset')
            print(f'method:{method},data:{folder}')
            provdector_test_multi(train_data_list, test_data_list)


if __name__ == "__main__":
    # result = detect(train_data='../../data/scenes/cve-2016-4971-small/normal/graph',
    #        test_data='../../data/scenes/cve-2016-4971-small/attack/graph')
    # print(result)
    multiprocessing.set_start_method('spawn')

    print(T, K, THRESHOLD)

    start_time = time.time()
    run_method_folder()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)
    # train_data_list = ['data/reduced_data_made/CPR/cve-2014-6271-multi/folder_1/train_dataset',
    #                    'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_2/train_dataset',
    #                    'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_3/train_dataset',
    #                    'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_4/train_dataset',
    #                    'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_5/train_dataset']
    # test_data_list = ['data/reduced_data_made/CPR/cve-2014-6271-multi/folder_1/test_dataset',
    #                   'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_2/test_dataset',
    #                   'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_3/test_dataset',
    #                   'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_4/test_dataset',
    #                   'data/reduced_data_made/CPR/cve-2014-6271-multi/folder_5/test_dataset']
    # provdector_test(train_data_list, test_data_list)

    # set_para(100, 10, 2)  # 设置论文中的时间窗口大小参数T、异常路径top数K、以及一张图中有多少路径判定为异常就告警
    #
    # train_dataset = 'cve-2016-4971_all/normal'
    # test_dataset = 'cve-2016-4971_all/attack'
    # # gt = 'APT-1(Community)/abnormal-v3-gt-apache.txt'
    # # train_dataset = 'vim_navigator/train'
    # # test_dataset = 'vim_navigator/test'
    # # gt = 'vim_navigator/gt.txt'
    #
    # # gt = os.path.join('dataset', gt)
    # train_file_name_list = os.listdir(train_path := os.path.join('data', train_dataset))
    # train_path_list = [os.path.join(train_path, i) for i in train_file_name_list]
    # test_file_name_list = os.listdir(test_path := os.path.join('data', test_dataset))
    # test_path_list = [os.path.join(test_path, i) for i in test_file_name_list]
    #
    #
    # # path_list = ['test1_old.txt',
    # #              'test2_old.txt',
    # #              'test2_old.txt']  # 数据路径，多个图的话就加入多条路径。文件每行的格式为(以空格隔开)：srcId srcType dstId dstType edgeType timestamp
    #
    # print(train_path_list + test_path_list)
    # G = graphBuilding(train_path_list + test_path_list)  # 构建数据源图
    # extraction(G, T)  # 提取所有图中边的表示数据
    #
    # print(train_path_list)
    # print(test_path_list)
    #
    # doc_ans_train = []
    # doc_ans_test = []
    # for i in range(len(G)):
    #     if i >= len(train_path_list):
    #         break
    #     print(f"working on train {i}: {train_path_list[i]}")
    #     doc_ans_train += work(G[i], K)  # 对于指定的图，计算路径异常指数并找到排名前K条边;训练时需要多张图的话，可以分别对每张图G[i]执行此操作，将结果合并到一个doc_ans中即可
    #
    # for i in range(len(G)):
    #     if i < len(train_path_list):
    #         continue
    #     print(f"working on test {i}: {test_path_list[i - len(train_path_list)]}")
    #     doc_ans_test += work(G[i], K)
    # print('work complete')
    #
    # train_vec, vec_ans = embedding(doc_ans_train, doc_ans_test, K)  # 路径特征嵌入，得到测试集中提取的每条路径各自的特征
    #
    # # exit(0)
    #
    # print("predict")
    # predict_ans = LOF(train_vec, vec_ans, doc_ans_train, doc_ans_test)  # 使用离群点检测算法得到每条路径的异常预测
    #
    # with open(f'result/train_{THRESHOLD}_{train_dataset.split("/")[0]}.txt', 'w') as f:
    #     for index, file_name in enumerate(train_file_name_list):
    #         doc = doc_ans_train[index * K: (index + 1) * K]
    #         for j in range(len(doc)):
    #             f.write(
    #                 f'{file_name}\t{str(doc[j])}\n')
    #
    # alert = []
    # with open(f'result/alert_{THRESHOLD}_{test_dataset.split("/")[0]}.txt', 'w') as f:
    #     for index, file_name in enumerate(test_file_name_list):
    #         detection = predict_ans[index * K: (index + 1) * K]
    #         doc = doc_ans_test[index * K: (index + 1) * K]
    #         for j in range(len(detection)):
    #             f.write(
    #                 f'{file_name}\t{str(np.count_nonzero((detection == -1)))}\t{str(detection[j])}\t{str(doc[j])}\n')
    #         if np.count_nonzero((detection == -1)) > THRESHOLD:
    #             alert.append(file_name.split('_')[1].split('.')[0])

    # with open(gt, 'r') as t:
    #     gts = set([i[:-1] for i in t.readlines()])
    #
    # tp = len(gts.intersection(set(alert)))
    # fp = len(set(alert).difference(gts))
    # fn = len(gts.difference(set(alert)))
    # tn = len(test_path_list) - len(set(alert).union(gts))
    # # print(gts)
    #
    # print('fp:', set(alert).difference(gts))
    # print('fn:', gts.difference(set(alert)))
    #
    # print('tp:', tp, 'fp:', fp, 'fn:',fn, 'tn:', tn, )
    # print("Accuracy: "+str(round((tp+tn)/(tp+fp+fn+tn), 3)))
    # print("Precision: ", precision := round((tp)/(tp+fp), 3))
    # print("Recall: ", recall := round((tp)/(tp+fn), 3))
    # print("F1Score: ", 2 * precision * recall /(precision + recall))
