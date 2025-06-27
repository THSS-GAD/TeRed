import math
import os
import re

import gensim
from Graph import *
import smart_open


def read_corpus(docs, K, tokens_only=False):
    def custom_tokenize(text):
        tokens = re.split(r'[ /:\\_.]', text)
        tokens = [token.strip() for token in tokens if token.strip()]
        return tokens

    for i in range(len(docs)):
        line = docs[i]

        pattern = r'sess_[a-zA-Z0-9]+ '
        replacement = 'sess_*'
        text = re.sub(pattern, replacement, line.lower())

        pattern = r'temp/[a-zA-Z0-9]+.php'
        replacement = 'temp/*.php'
        text = re.sub(pattern, replacement, text)

        pattern = r'::ffff:'
        replacement = ''
        line = re.sub(pattern, replacement, text)

        tokens = gensim.utils.simple_preprocess(line, deacc=True)
        # print(tokens)
        # tokens = custom_tokenize(line)
        # print(tokens)
        # tokens = list(line)
        # print("tokens", tokens)
        if tokens_only:
            yield tokens
        else:
            yield gensim.models.doc2vec.TaggedDocument(tokens, [int(i/K)])


def embedding(train_docs, test_docs, K):
    train_corpus = list(read_corpus(train_docs,K))

    # print("now embedding, train corpus")
    model = gensim.models.doc2vec.Doc2Vec(vector_size=100, min_count=2, epochs=50)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)
    train_vec = []
    ans_vec = []

    # print("train complete")
    # print("doc2vec:(train&test)")
    for i in list(read_corpus(train_docs,K, tokens_only=True)):
        vector = model.infer_vector(i)
        train_vec.append(vector)
    for i in list(read_corpus(test_docs,K, tokens_only=True)):
        vector = model.infer_vector(i)
        ans_vec.append(vector)
    return train_vec, ans_vec
