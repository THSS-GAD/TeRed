import argparse
import datetime
import json
import os
import shutil
import sys
import uuid


def load_graph(path: str):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)


def string_to_ts(string: str) -> float:
    a, b = string.split(".")
    string = f"{a}.{b[:6]}"
    dt = datetime.time.fromisoformat(string)
    return dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1000000


class NodeDict(dict):
    def __missing__(self, key):
        self[key] = len(self)
        return self[key]


def hashgen(val: str) -> str:
    # return uuid.uuid5(uuid.NAMESPACE_DNS, val)
    return hash(val) % 2 ** sys.hash_info.width


def parse(src_path: str, output_dir: str = "tmp"):
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    graph = load_graph(src_path)
    mid = int(len(graph["links"]) * 0.1)

    prev_nodes = NodeDict()
    it = iter(
        enumerate(sorted(graph["links"], key=lambda x: string_to_ts(x["ts"]))))

    # FIXME: Edge direction?

    with open(os.path.join(output_dir, "normal.txt"), "w") as f:
        for _ in range(mid):
            ts, event = next(it)
            f.write(f"{prev_nodes[event['source']]}\t{prev_nodes[event['target']]}\t"
                    f"{hashgen(event['source_type'])}:{hashgen(event['target_type'])}:"
                    f"{hashgen(event['syscall'])}:{ts}\n")

    with open(os.path.join(output_dir, "stream.txt"), "w") as f:
        for ts, event in it:
            src_unseen, dst_unseen = 0, 0
            if event["source"] not in prev_nodes:
                src_unseen = 1
            if event["target"] not in prev_nodes:
                dst_unseen = 1

            f.write(f"{prev_nodes[event['source']]}\t{prev_nodes[event['target']]}\t"
                    f"{hashgen(event['source_type'])}:{hashgen(event['target_type'])}:"
                    f"{hashgen(event['syscall'])}:{src_unseen}:{dst_unseen}:{ts}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    parser.add_argument("-o", "--output", type=str, default="tmp")
    args = parser.parse_args()

    parse(args.path, args.output)
