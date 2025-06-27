#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : lxx
# @time    : 2023/12/28 16:15
# @function: main file for the reduce scripts.
# @version : V1

import os
import shutil
import multiprocessing
from settings import COMPRESSED_FOLDER
from reduction_set.graph_match_and_replace import match_and_replace
from reduction_set.gspan_mining.data_processing import get_filelists_indir

# # 压缩阶段，对大图进行子图匹配并完成替换
# def reduce_by_template(log_compress, template_dir):
#     # 确保目标文件夹存在，如果不存在则创建
#     os.makedirs(COMPRESSED_FOLDER, exist_ok=True)
#     # 将源文件复制到目标文件夹中
#     shutil.copy(log_compress, COMPRESSED_FOLDER)
#     template_files = get_filelists_indir(template_dir)
#     for file in template_files:
#         print(file)
#         process = multiprocessing.Process(target=match_and_replace, args=(log_compress, file))
#         # 启动进程
#         process.start()

#         # 设置超时时间为10秒
#         timeout = 5

#         # 等待进程结束，最多等待timeout秒
#         process.join(timeout)

#         # 如果进程仍在运行，就终止它
#         if process.is_alive():
#             print("函数执行超时，将终止进程")
#             process.terminate()
#             process.join()  # 等待进程真正结束
#             continue  # 继续下一循环

#         print("函数执行完成")

def reduce_by_template(log_compress, template_dir):
    # 确保目标文件夹存在
    os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

    # 获取原日志文件名（不含路径）
    filename = os.path.basename(log_compress)

    # 构造压缩目录下的完整路径
    compressed_log_path = os.path.join(COMPRESSED_FOLDER, filename)

    # 拷贝日志文件到压缩目录
    shutil.copy(log_compress, compressed_log_path)

    # 获取所有模板文件
    template_files = get_filelists_indir(template_dir)

    # 遍历模板并对 compressed_output 中的日志进行压缩
    for file in template_files:
        print(f"Using template: {file}")
        
        process = multiprocessing.Process(
            target=match_and_replace, 
            args=(compressed_log_path, file)
        )
        process.start()

        timeout = 5
        process.join(timeout)

        if process.is_alive():
            print("函数执行超时，将终止进程")
            process.terminate()
            process.join()
            continue

        print("函数执行完成")



