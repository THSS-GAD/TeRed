#!/usr/bin/python
# -*- coding:utf-8 -*-
# @function: process sysdig log files and generate graph data.
import argparse
import re

import networkx as nx
from loguru import logger


def _get_fd_type(fd_type_str):
    if fd_type_str == "f":
        return "file"
    elif fd_type_str == "d":
        return "dir"
    elif fd_type_str == "p":
        return "pipe"
    elif fd_type_str.startswith("4"):
        return "ipv4_socket"
    elif fd_type_str.startswith("6"):
        return "ipv6_socket"
    elif fd_type_str == "u":
        return "unix_socket"
    else:
        logger.debug(f"unknown fd_type: {fd_type_str}")
        return "unknown"


def _get_f_path(f_path_from_regex):
    # regex 可能提取 None
    if f_path_from_regex is None:
        return None
    # 使用括号内的部分，主要是处理类似于这样的特殊情况
    # /tmp/wget-1.17/testenv/Redirection crash-test/127.0.0.1:42707/File formats/Images/SVG, Scalable Vector Graphics/html, W3C v1.2 rec (tiny)/directory
    if "(/" in f_path_from_regex:
        f_path_from_regex = "/" + f_path_from_regex[:-1].split("(/")[1]
    return f_path_from_regex


# Proc Start : <
SYSCALL_PROC_START = ["fork", "vfork", "clone"]
REGEX_PROC_START = re.compile(
    r".*exe=(?P<exe>.*) args.*pid=(?P<pid>\d*)\(.* ptid=(?P<ppid>\d*)\((?P<ppname>.*)\) cwd=.*flags=(?P<flags>.*) uid=(?P<uid>\d*) gid=(?P<gid>\d*).*",
    re.DOTALL,
)
# Proc End
# Active : >
SYSCALL_PROC_END_ACTIVE = ["procexit"]
REGEX_PROC_END_ACTIVE = re.compile(
    r"status=(?P<status>\d*) ret=(?P<ret>\d*).*", re.DOTALL
)
# TODO: Passive Proc End
#   Passive : > (& < if consider success)
#   SYSCALL_PROC_END_PASSIVE = ['kill', 'tkill', 'tgkill']
# File Exec : <
SYSCALL_FILE_EXEC = ["execve"]
REGEX_FILE_EXEC = re.compile(
    r"res=(?P<res>.*) exe=(?P<exe>.*) args.*pid=(?P<pid>\d*)\(.* ptid=(?P<ppid>\d*)\((?P<ppname>.*)\) cwd=.*flags=(?P<flags>.*).*",
    re.DOTALL,
)
# File Open (for creation) : <
SYSCALL_FILE_OPEN = ["open", "openat", "openat2"]
REGEX_FILE_OPEN = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>.*)\))? dirfd=.*flags=(?P<flags>.*) mode=.*",
    re.DOTALL,
)
REGEX_DIR_OPEN = re.compile(
    r"dirfd=(?P<fd_num>.*) name=(?P<fd_content>.*) flags=(?P<flags>.*) mode=.*",
    re.DOTALL,
)
# TODO: File Creat : <
SYSCALL_FILE_CREAT = ["creat"]
REGEX_FILE_CREAT = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>[^()]*)\))?.*mode=.*",
    re.DOTALL,
)
# File Del : <
SYSCALL_FILE_DEL = ["unlink", "unlinkat"]
REGEX_FILE_DEL_UNLINK = re.compile(r"res=(?P<res>\d*) path=(?P<path>.*)", re.DOTALL)
REGEX_FILE_DEL_UNLINKAT = re.compile(
    r"res=(?P<res>\d*).*name=(?P<name>.*) flags=.*", re.DOTALL
)
# File (& Socket) Write : > & <
SYSCALL_FILE_WRITE = [
    "write",
    "pwrite",
    "writev",
    "pwritev",
    "send",
    "sendto",
    "sendmsg",
]
REGEX_FILE_WRITE_ARGS = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>.*)\))? size=.*",
    re.DOTALL,
)
REGEX_FILE_WRITE_ARGS_BAK = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>.*)\))?.*",
    re.DOTALL,
)
REGEX_FILE_WRITE_RES = re.compile(r"res=(?P<res>\d*).*", re.DOTALL)
# File (& Socket) Read : > & <
SYSCALL_FILE_READ = [
    "read",
    "pread",
    "readv",
    "preadv",
    "recv",
    "recvfrom",
    "recvmsg",
]
REGEX_FILE_READ_ARGS = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>.*)\))? size=.*",
    re.DOTALL,
)
REGEX_FILE_READ_ARGS_BAK = re.compile(
    r"fd=(?P<fd_num>[-\d]*)\(?(<(?P<fd_type>\w{1,2})>)?((?P<fd_content>.*)\))?.*",
    re.DOTALL,
)
REGEX_FILE_READ_RES = re.compile(r"res=(?P<res>\d*).*", re.DOTALL)


def _build_graph(log_file, ignore_no_return=False, container_mode=True):
    # (uni_pid | uni_path) -> (Process | File)
    # Process: pid,pname,host
    # File: path,type,host
    entities = dict()
    # (src,dst,dict(ts,syscall,success))[]
    events = []
    write_stack = []
    read_stack = []
    with open(log_file) as fh:
        for line in fh:
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # norm
            # if not in container mode, localhost is the default host
            if container_mode:
                (
                    _,
                    ts,
                    _,
                    container_name,
                    _,
                    pname,
                    pid_str,
                    syscall_dir,
                    syscall,
                    *syscall_args,
                ) = line.split(" ")
                pid, _ = pid_str[1:-1].split(":")
            else:
                (
                    _,
                    ts,
                    _,
                    pname,
                    pid_str,
                    syscall_dir,
                    syscall,
                    *syscall_args,
                ) = line.split(" ")
                container_name = "localhost"
                pid = pid_str[1:-1]
            uni_pid = pname + "__" + pid
            syscall_args = " ".join(syscall_args)

            if syscall_dir == ">":
                if syscall in SYSCALL_PROC_END_ACTIVE:
                    res = REGEX_PROC_END_ACTIVE.match(syscall_args)
                    if res:
                        success = res.group("ret") == "0"
                        if uni_pid not in entities:
                            entities[uni_pid] = dict(
                                pid=pid,
                                pname=pname,
                                type="process",
                                host=container_name,
                            )
                        events.append(
                            (
                                uni_pid,
                                "",
                                dict(
                                    ts=ts,
                                    syscall=syscall,
                                    success=success,
                                    source_type=entities[uni_pid]["type"],
                                    target_type="",
                                ),
                            )
                        )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_WRITE:
                    res = REGEX_FILE_WRITE_ARGS.match(syscall_args)
                    if res:
                        f_type = res.group("fd_type")
                        f_path = res.group("fd_content")
                        f_path = _get_f_path(f_path)
                        write_stack.append(
                            (ts, container_name, uni_pid, pid, syscall, f_type, f_path)
                        )
                    else:
                        res = REGEX_FILE_WRITE_ARGS_BAK.match(syscall_args)
                        if res:
                            f_type = res.group("fd_type")
                            f_path = res.group("fd_content")
                            f_path = _get_f_path(f_path)
                            write_stack.append(
                                (
                                    ts,
                                    container_name,
                                    uni_pid,
                                    pid,
                                    syscall,
                                    f_type,
                                    f_path,
                                )
                            )
                        else:
                            logger.debug(
                                f"syscall: `{syscall}`, args: `{syscall_args}`"
                            )
                elif syscall in SYSCALL_FILE_READ:
                    res = REGEX_FILE_READ_ARGS.match(syscall_args)
                    if res:
                        f_type = res.group("fd_type")
                        f_path = res.group("fd_content")
                        f_path = _get_f_path(f_path)
                        read_stack.append(
                            (ts, container_name, uni_pid, pid, syscall, f_type, f_path)
                        )
                    else:
                        res = REGEX_FILE_READ_ARGS_BAK.match(syscall_args)
                        if res:
                            f_type = res.group("fd_type")
                            f_path = res.group("fd_content")
                            f_path = _get_f_path(f_path)
                            read_stack.append(
                                (
                                    ts,
                                    container_name,
                                    uni_pid,
                                    pid,
                                    syscall,
                                    f_type,
                                    f_path,
                                )
                            )
                        else:
                            logger.debug(
                                f"syscall: `{syscall}`, args: `{syscall_args}`"
                            )
                elif syscall in SYSCALL_FILE_OPEN:
                    # CHECKME: 这些行为不一定有意义，理论上可以删掉，但为了构图的完整性还是保留，可以通过参数控制
                    if ignore_no_return:
                        continue
                    # 有一些针对目录的 openat 没有返回，在这里处理
                    # 格式类似于：`openat dirfd=-100(AT_FDCWD) name=.(/home) flags=13377(O_DIRECTORY|O_NONBLOCK|O_RDONLY|O_CLOEXEC|O_TMPFILE) mode=0`
                    res = REGEX_DIR_OPEN.match(syscall_args)
                    if res:
                        fd_num = res.group("fd_num")
                        # 使用相对路径也会返回负数，需要特判
                        success = "AT_FDCWD" in fd_num or "-" not in fd_num
                        # 不成功的也打不开，没什么意义
                        if success:
                            f_path = res.group("fd_content")
                            f_path = _get_f_path(f_path)
                            # 从相对路径中解析绝对路径
                            if "(" in f_path:
                                f_path = f_path[:-1].split("(")[1]
                            uni_f_path = container_name + "__" + f_path
                            if uni_pid not in entities:
                                entities[uni_pid] = dict(
                                    pid=pid,
                                    pname=pname,
                                    type="process",
                                    host=container_name,
                                )
                            if uni_f_path not in entities:
                                entities[uni_f_path] = dict(
                                    path=f_path,
                                    type=_get_fd_type("d"),
                                    host=container_name,
                                )
                            events.append(
                                (
                                    uni_pid,
                                    uni_f_path,
                                    dict(
                                        ts=ts,
                                        syscall=syscall,
                                        success=True,
                                        source_type=entities[uni_pid]["type"],
                                        target_type=entities[uni_f_path]["type"],
                                    ),
                                )
                            )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")

            if syscall_dir == "<":
                if syscall in SYSCALL_PROC_START:
                    res = REGEX_PROC_START.match(syscall_args)
                    if res:
                        ppid = res.group("ppid")
                        ppname = res.group("ppname")
                        uni_ppid = ppname + "__" + ppid
                        if uni_ppid not in entities:
                            entities[uni_ppid] = dict(
                                pid=ppid,
                                pname=ppname,
                                type="process",
                                host=container_name,
                            )
                        if uni_pid not in entities:
                            entities[uni_pid] = dict(
                                pid=pid,
                                pname=pname,
                                type="process",
                                host=container_name,
                            )
                        events.append(
                            (
                                uni_ppid,
                                uni_pid,
                                dict(
                                    ts=ts,
                                    syscall=syscall,
                                    success=True,
                                    source_type=entities[uni_ppid]["type"],
                                    target_type=entities[uni_pid]["type"],
                                ),
                            )
                        )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_EXEC:
                    res = REGEX_FILE_EXEC.match(syscall_args)
                    if res:
                        success = "-" not in res.group("res")
                        ppid = res.group("ppid")
                        ppname = res.group("ppname")
                        uni_ppid = ppname + "__" + ppid
                        if uni_ppid not in entities:
                            entities[uni_ppid] = dict(
                                pid=ppid,
                                pname=ppname,
                                type="process",
                                host=container_name,
                            )
                        if uni_pid not in entities:
                            entities[uni_pid] = dict(
                                pid=pid,
                                pname=pname,
                                type="process",
                                host=container_name,
                            )
                        events.append(
                            (
                                uni_ppid,
                                uni_pid,
                                dict(
                                    ts=ts,
                                    syscall=syscall,
                                    success=success,
                                    source_type=entities[uni_ppid]["type"],
                                    target_type=entities[uni_pid]["type"],
                                ),
                            )
                        )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_OPEN:
                    res = REGEX_FILE_OPEN.match(syscall_args)
                    if res:
                        success = "-" not in res.group("fd_num")
                        # 不成功的也打不开，没什么意义
                        if success:
                            f_type = res.group("fd_type")
                            f_path = res.group("fd_content")
                            f_path = _get_f_path(f_path)
                            # Ignore some special cases
                            if f_path is None:
                                logger.debug(
                                    f"syscall: `{syscall}`, args: `{syscall_args}`"
                                )
                                continue
                            uni_f_path = container_name + "__" + f_path
                            if uni_pid not in entities:
                                entities[uni_pid] = dict(
                                    pid=pid,
                                    pname=pname,
                                    type="process",
                                    host=container_name,
                                )
                            if uni_f_path not in entities:
                                entities[uni_f_path] = dict(
                                    path=f_path,
                                    type=_get_fd_type(f_type),
                                    host=container_name,
                                )
                            events.append(
                                (
                                    uni_pid,
                                    uni_f_path,
                                    dict(
                                        ts=ts,
                                        syscall=syscall,
                                        success=True,
                                        source_type=entities[uni_pid]["type"],
                                        target_type=entities[uni_f_path]["type"],
                                    ),
                                )
                            )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_CREAT:
                    res = REGEX_FILE_CREAT.match(syscall_args)
                    if res:
                        success = "-" not in res.group("fd_num")
                        f_type = res.group("fd_type")
                        f_path = res.group("fd_content")
                        f_path = _get_f_path(f_path)
                        uni_f_path = container_name + "__" + f_path
                        if uni_pid not in entities:
                            entities[uni_pid] = dict(
                                pid=pid,
                                pname=pname,
                                type="process",
                                host=container_name,
                            )
                        if uni_f_path not in entities:
                            entities[uni_f_path] = dict(
                                path=f_path,
                                type=_get_fd_type(f_type),
                                host=container_name,
                            )
                        events.append(
                            (
                                uni_pid,
                                uni_f_path,
                                dict(
                                    ts=ts,
                                    syscall=syscall,
                                    success=success,
                                    source_type=entities[uni_pid]["type"],
                                    target_type=entities[uni_f_path]["type"],
                                ),
                            )
                        )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_DEL:
                    res = REGEX_FILE_DEL_UNLINK.match(syscall_args)
                    if res:
                        success = "-" not in res.group("res")
                        f_path = res.group("path")
                        f_path = _get_f_path(f_path)
                        uni_f_path = container_name + "__" + f_path
                        if uni_pid not in entities:
                            entities[uni_pid] = dict(
                                pid=pid,
                                pname=pname,
                                type="process",
                                host=container_name,
                            )
                        events.append(
                            (
                                uni_pid,
                                uni_f_path,
                                dict(
                                    ts=ts,
                                    syscall=syscall,
                                    success=success,
                                    source_type=entities[uni_pid]["type"],
                                    target_type=entities[uni_f_path]["type"],
                                ),
                            )
                        )
                    else:
                        res = REGEX_FILE_DEL_UNLINKAT.match(syscall_args)
                        if res:
                            success = "-" not in res.group("res")
                            f_path = res.group("name")
                            f_path = _get_f_path(f_path)
                            uni_f_path = container_name + "__" + f_path
                            if uni_pid not in entities:
                                entities[uni_pid] = dict(
                                    pid=pid,
                                    pname=pname,
                                    type="process",
                                    host=container_name,
                                )
                            if uni_f_path not in entities:
                                entities[uni_f_path] = dict(
                                    path=f_path,
                                    type=_get_fd_type(f_type),
                                    host=container_name,
                                )
                            events.append(
                                (
                                    uni_pid,
                                    uni_f_path,
                                    dict(
                                        ts=ts,
                                        syscall=syscall,
                                        success=success,
                                        source_type=entities[uni_pid]["type"],
                                        target_type=entities[uni_f_path]["type"],
                                    ),
                                )
                            )
                        else:
                            logger.debug(
                                f"syscall: `{syscall}`, args: `{syscall_args}`"
                            )
                elif syscall in SYSCALL_FILE_WRITE:
                    res = REGEX_FILE_WRITE_RES.match(syscall_args)
                    if res:
                        if write_stack:
                            (
                                ts,
                                container_name,
                                uni_pid,
                                pid,
                                syscall,
                                f_type,
                                f_path,
                            ) = write_stack.pop()
                            success = "-" not in res.group("res")
                            # 压栈时已处理过 f_path，这里不再处理
                            if f_path:
                                if _get_fd_type(f_type) in [
                                    "ipv4 socket",
                                    "ipv6 socket",
                                ]:
                                    sock_pair = f_path.split("->")
                                    if len(sock_pair) == 2:
                                        f_path = sock_pair[1]
                                uni_f_path = container_name + "__" + f_path
                                if uni_pid not in entities:
                                    entities[uni_pid] = dict(
                                        pid=pid,
                                        pname=pname,
                                        type="process",
                                        host=container_name,
                                    )
                                if uni_f_path not in entities:
                                    entities[uni_f_path] = dict(
                                        path=f_path,
                                        type=_get_fd_type(f_type),
                                        host=container_name,
                                    )
                                events.append(
                                    (
                                        uni_pid,
                                        uni_f_path,
                                        dict(
                                            ts=ts,
                                            syscall=syscall,
                                            success=success,
                                            source_type=entities[uni_pid]["type"],
                                            target_type=entities[uni_f_path]["type"],
                                        ),
                                    )
                                )
                        else:
                            logger.debug(
                                f"syscall: `{syscall}`, args: `{syscall_args}`"
                            )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")
                elif syscall in SYSCALL_FILE_READ:
                    res = REGEX_FILE_READ_RES.match(syscall_args)
                    if res:
                        if read_stack:
                            (
                                ts,
                                container_name,
                                uni_pid,
                                pid,
                                syscall,
                                f_type,
                                f_path,
                            ) = read_stack.pop()
                            success = "-" not in res.group("res")
                            # 压栈时已处理过 f_path，这里不再处理
                            if f_path:
                                if _get_fd_type(f_type) in [
                                    "ipv4 socket",
                                    "ipv6 socket",
                                ]:
                                    sock_pair = f_path.split("->")
                                    if len(sock_pair) == 2:
                                        f_path = sock_pair[1]
                                uni_f_path = container_name + "__" + f_path
                                if uni_pid not in entities:
                                    entities[uni_pid] = dict(
                                        pid=pid,
                                        pname=pname,
                                        type="process",
                                        host=container_name,
                                    )
                                if uni_f_path not in entities:
                                    entities[uni_f_path] = dict(
                                        path=f_path,
                                        type=_get_fd_type(f_type),
                                        host=container_name,
                                    )
                                events.append(
                                    (
                                        uni_pid,
                                        uni_f_path,
                                        dict(
                                            ts=ts,
                                            syscall=syscall,
                                            success=success,
                                            source_type=entities[uni_pid]["type"],
                                            target_type=entities[uni_f_path]["type"],
                                        ),
                                    )
                                )
                        else:
                            logger.debug(
                                f"syscall: `{syscall}`, args: `{syscall_args}`"
                            )
                    else:
                        logger.debug(f"syscall: `{syscall}`, args: `{syscall_args}`")

    logger.info(f"no return write: `{write_stack}`")
    logger.info(f"no return read: `{read_stack}`")
    logger.info(f"{len(entities)} entities and {len(events)} events")

    g = nx.DiGraph()
    entities = entities.items()
    events = list(filter(lambda e: e[2]["syscall"] != "procexit", events))
    g.add_nodes_from(entities)
    g.add_edges_from(events)
    # logger.info(g)

    return g, list(entities), list(events)


def read_sysdig_log(log_file):
    # 根据实际日志格式使用正则表达式等方式提取相关信息
    # 返回图数据，可以使用networkx等库构建图
    prov_graph, _, _ = _build_graph(log_file, ignore_no_return=True)
    return prov_graph


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-L", "--log", required=True)
    args = parser.parse_args()

    read_sysdig_log(args.log)
