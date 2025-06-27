#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : lxx
# @time    : 2023/11/28 16:38
# @function: processing graph data and mining subgraph.
# @version : V1

import os
import sys

from settings import DATA_DIR, TEMPLATE_DIR
from .config import parser
from .gspan import gSpan
from .data_processing import process_json_files,output_json_file

def run_gSpan(FLAGS=None):
    """Run gSpan."""

    if FLAGS is None:
        FLAGS, _ = parser.parse_known_args(args=sys.argv[1:])

    if not os.path.exists(FLAGS.database_file_name):
        print('{} does not exist.'.format(FLAGS.database_file_name))
        sys.exit()

    gs = gSpan(
        database_file_name=FLAGS.database_file_name,
        min_support=FLAGS.min_support,
        min_num_vertices=FLAGS.lower_bound_of_num_vertices,
        max_num_vertices=FLAGS.upper_bound_of_num_vertices,
        max_ngraphs=FLAGS.num_graphs,
        is_undirected=(not FLAGS.directed),
        verbose=FLAGS.verbose,
        visualize=FLAGS.plot,
        where=FLAGS.where
    )

    gs.run()
    gs.time_stats()
 
    return gs



def mine_subgraph(graph_data):
    graph_data_file = process_json_files(graph_data)
    # 返回得到的模板子图
    args_str = '-s 5 -d True ' + graph_data_file
    FLAGS, _ = parser.parse_known_args(args=args_str.split())
    print("——————————子图挖掘————————————")
    output_subgraph_file = 'reduction_set/gspan_mining/subgraph_'+graph_data+'.txt'
    sys.stdout = open(output_subgraph_file, 'w')
    run_gSpan(FLAGS)
    sys.stdout = sys.__stdout__
    print("——————子图挖掘结束——————————")
    output_json = TEMPLATE_DIR +'freq_'+ graph_data +'.json'
    print(output_json)
    output_json_file(output_subgraph_file,output_json)
    return output_json


