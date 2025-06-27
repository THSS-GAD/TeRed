#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : lxx
# @time    : 2023/11/28 16:32
# @function: main
# @version : V1

from settings import DATA_TO_COMPRESS, DATA_TO_LEARN, TEMPLATE_DIR
from reduction_set.reduce_by_template import reduce_by_template
from reduction_set.gspan_mining.graph_mining import mine_subgraph

def learn_and_compress(log_learn, log_compress):
    # learn stage
    mine_subgraph(log_learn)

    # reduce stage
    reduce_by_template(log_compress,TEMPLATE_DIR)


if __name__ == "__main__":
    learn_and_compress(DATA_TO_LEARN, DATA_TO_COMPRESS)