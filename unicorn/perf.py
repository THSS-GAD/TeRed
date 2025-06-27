import argparse
import re


def get_max(perf_file, fold=5):
    metrics = ["mean", "max"]
    history = {"mean": dict(), "max": dict()}
    f1_dict = {"mean": dict(), "max": dict()}
    f1_metric = ""
    f1_std = ""
    with open(perf_file) as perf_fh:
        for line in perf_fh:
            # init
            if line.startswith("Metric"):
                metric_std_reg = re.compile(
                    "Metric: (?P<metric>[^ ]*) STD: (?P<std>[^ ]*)"
                )
                metric_std_match_dict = metric_std_reg.match(line).groupdict()
                f1_metric = metric_std_match_dict["metric"]
                f1_std = float(metric_std_match_dict["std"])
                f1_dict[f1_metric].setdefault(f1_std, 0)
                history[f1_metric].setdefault(f1_std, [])
            if line.startswith("Accuracy"):
                res_reg = re.compile(
                    "Accuracy: (?P<accuracy>[^ ]*)\tPrecision: (?P<precision>[^ ]*)\tRecall: (?P<recall>[^ ]*)\tF-1: (?P<f1>[^ ]*)"
                )
                res_dict = res_reg.match(line.strip()).groupdict()
                current_f1 = float(res_dict["f1"]) if res_dict["f1"] != "None" else 0
                f1_dict[f1_metric][f1_std] += current_f1 / fold
                history[f1_metric][f1_std].append(line.strip())

    max_f1 = 0
    max_f1_metric = ""
    max_f1_std = ""
    for metric in metrics:
        for std in f1_dict[metric].keys():
            f1 = f1_dict[metric][std]
            if f1 > max_f1:
                max_f1 = f1
                max_f1_metric = metric
                max_f1_std = std
    return max_f1_metric, max_f1_std, max_f1, history[max_f1_metric][max_f1_std]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-log", required=True)
    args = parser.parse_args()

    max_f1_metric, max_f1_std, max_f1, histroy = get_max(args.input_log)
    print(max_f1_metric, max_f1_std, max_f1)
    for item in histroy:
        print(item)
