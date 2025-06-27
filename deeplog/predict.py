import sys
sys.path.append('../')
import json
import logging
import argparse
from deeplog.deeplog import model_fn, input_fn, predict_fn

logging.basicConfig(level=logging.WARNING,
                    format='[%(asctime)s][%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

def model_predict(threshold,dir):
    # logging.basicConfig(level=logging.WARNING,
    #                 format='[%(asctime)s][%(levelname)s]: %(message)s')
    # logger = logging.getLogger(dir)
    # fh = logging.FileHandler(dir+'/predict_result_'+str(threshold)+'.log')  # 这里的"log_file.log"是你的日志文件名，可以根据你的需要更改
    # fh.setLevel(logging.INFO)
    # logger.addHandler(fh)
    logfile = open(dir+'/predict_result_'+str(threshold)+'.log', "w")
    # logger.addHandler(logging.StreamHandler(sys.stdout))

    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', type=int, default=threshold, metavar='N',
                        help='to determine the time series data is an anomaly or not.')
    args = parser.parse_args()

    ##############
    # Load Model #
    ##############
    model_dir = dir
    model_info = model_fn(model_dir)

    ###########
    # predict #
    ###########
    test_abnormal_list = []
    with open(dir+'/test_abnormal', 'r') as f:
        for line in f.readlines():
            line = list(map(lambda n: n - 1, map(int, line.strip().split())))
            request = json.dumps({'line': line})
            input_data = input_fn(request, 'application/json')
            response = predict_fn(input_data, model_info)
            test_abnormal_list.append(response)

    test_normal_list = []
    with open(dir+'/test_normal', 'r') as f:
        for line in f.readlines():
            line = list(map(lambda n: n - 1, map(int, line.strip().split())))
            request = json.dumps({'line': line})
            input_data = input_fn(request, 'application/json')
            response = predict_fn(input_data, model_info)
            test_normal_list.append(response)

    ##############
    # Evaluation #
    ##############
    thres = args.threshold
    abnormal_has_anomaly = [1 if t['anomaly_cnt'] > thres else 0 for t in test_abnormal_list]
    # for t in test_abnormal_list:
    #     print("test_abnormal_list:",t['anomaly_cnt'])
    abnormal_cnt_anomaly = [t['anomaly_cnt'] for t in test_abnormal_list]
    abnormal_predict = []
    for test_abnormal in test_abnormal_list:
        abnormal_predict += test_abnormal['predict_list']

    normal_has_anomaly = [1 if t['anomaly_cnt'] > thres else 0 for t in test_normal_list]
    normal_cnt_anomaly = [t['anomaly_cnt'] for t in test_normal_list]
    normal_predict = []
    for test_normal in test_normal_list:
        normal_predict += test_normal['predict_list']

    ground_truth = [1]*len(abnormal_has_anomaly) + [0]*len(normal_has_anomaly)
    predict = abnormal_has_anomaly + normal_has_anomaly
    # print("abnormal_has_anomaly: ",abnormal_has_anomaly)
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    accu = 0
    for p, t in zip(predict, ground_truth):
        if p == t:
            accu += 1

        if p == 1 and t == 1:
            TP += 1
        elif p == 1 and t == 0:
            FP += 1
        elif p == 0 and t == 1:
            FN += 1
        else:
            TN += 1

    logfile.write(f'thres: {thres}\n')
    logfile.write(f'TP: {TP}\n')
    logfile.write(f'FP: {FP}\n')
    logfile.write(f'TN: {TN}\n')
    logfile.write(f'FN: {FN}\n')

    accuracy = accu / len(predict)
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    F1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    logfile.write(f'accuracy: {accuracy}\n')
    logfile.write(f'Precision: {precision}\n')
    logfile.write(f'Recall: {recall}\n')
    logfile.write(f'F1: {F1}')
