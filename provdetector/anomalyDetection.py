import pandas as pd
import numpy as np
import plotly.express as px
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from sklearn.neighbors import LocalOutlierFactor


def LOF(train_vec, vec_ans, doc_train, doc_ans):
    data_train = train_vec
    data = vec_ans
    clf = LocalOutlierFactor(n_neighbors=2, algorithm='auto', leaf_size=30, metric='minkowski', p=2, metric_params=None,
                             n_jobs=4, novelty=True)
    clf = clf.fit(data_train)
    predict = clf.predict(data)
    negative_outlier_factor = clf.negative_outlier_factor_

    x = np.array(train_vec + vec_ans)
    train_and_predict = np.concatenate((np.zeros(shape=(len(train_vec))), predict), axis=None)
    tsne = TSNE(n_components=2, perplexity=30)
    x_tsne = tsne.fit_transform(x)

    # print(x_tsne.shape)
    # print(len(doc_ans))
    # print()
    data = pd.DataFrame({
        'x': x_tsne[:, 0],
        'y': x_tsne[:, 1],
        'predict': train_and_predict,
        'text': doc_train + doc_ans
    })

    # print(data)
    # exit()
    # fig = px.scatter(data, x='x', y='y', hover_data=['text'], color='predict')

    # # 添加悬停提示
    # fig.update_traces(
    #     hovertext=data['text'],  # 属性信息显示在悬停提示中
    #     hoverinfo='text'  # 显示文本信息
    # )

    # fig.show()

    # 设置图表布局

    # plt.figure(figsize=(8, 8))
    #
    # plt.scatter(x_tsne[train_and_predict == 0, 0], x_tsne[train_and_predict == 0, 1], c='#576690', s=5, alpha=0.7, label='Train Set')
    # plt.scatter(x_tsne[train_and_predict == -1, 0], x_tsne[train_and_predict == -1, 1], c='red', s=5, alpha=0.7,label='Test Set(alert)')
    # plt.scatter(x_tsne[train_and_predict == 1, 0], x_tsne[train_and_predict == 1, 1], c='#9AC8E2', s=5,alpha=0.7, label='Test Set(safe)')
    #
    # plt.title("Local Outlier Factor (LOF)")
    # plt.legend()
    # plt.savefig('result/lof_provdetector.svg')
    # plt.show()

    return predict
