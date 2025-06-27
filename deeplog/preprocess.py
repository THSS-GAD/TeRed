import os
import sys
import logging
import pandas as pd
from spellpy import spell
from datetime import datetime, timedelta
logging.basicConfig(level=logging.WARNING,
                    format='[%(asctime)s][%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

def parse_time(s):
    try:
        dt = pd.to_datetime(s.astype(int) // 1000000000, unit='s')
        # 尝试解析纳秒时间戳
        # ts = int(s)
        # ts = ts / 10**9  # 从纳秒转为秒
        # dt = datetime.fromtimestamp(ts)
        return dt
    except (TypeError, ValueError) :
        pass

    try:
        # 尝试解析"%H:%M:%S.%f"格式的时间字符串
        return pd.to_datetime(s)
    except ValueError as err:
        print(s)
        # 如果都不匹配，抛出错误
        raise ValueError("无法解析时间格式: {}".format(err))

def parse_date_column_safe(time_series):
    def convert(t):
        t = str(t).zfill(6)[:6]  # 确保长度为6（截断过长）
        try:
            return datetime.strptime(t, "%H%M%S").time()
        except ValueError:
            return pd.NaT  # 无法解析则置为 NaT
    return time_series.apply(convert)

# def deeplog_df_transfer(df, event_id_map):
#     # df['datetime'] = pd.to_datetime(str(df['Date']) + ' ' + str(df['Time']))
#     # print(df.head())
#     print(df['Date'])
#     # 将日期列转为 datetime
#       # 将日期列转为 datetime
#     df['Date'] = pd.to_datetime(df['Date'])

#     # 将时间戳列转为 datetime，提取时间部分
#     df['Time'] = pd.to_datetime(df['Time'].astype(int) // 1000000000, unit='s').dt.time
#     # df['Time'] = pd.to_datetime(df['Time'].astype(str) // 1000000000, unit='s').dt.time

#     # 将日期和时间合并为新的datetime列
#     df['datetime'] = pd.to_datetime(df['Date'].dt.date.astype(str) + ' ' + df['Time'].astype(str))

#     df = df[['datetime', 'EventId']]
#     df['EventId'] = df['EventId'].apply(lambda e: event_id_map[e] if event_id_map.get(e) else -1)
    
#     deeplog_df = df.set_index('datetime').resample('1s').apply(_custom_resampler).dropna().reset_index()
#     # deeplog_df= df.set_index('datetime').reset_index()
#     deeplog_df = deeplog_df[deeplog_df['EventId'].apply(len) > 0]
#     # print(deeplog_df)
#     return deeplog_df


def left_shift_row_if_invalid_date(row):
    try:
        pd.to_datetime(row['Date'])
        return row
    except Exception:
        # 将该行数据左移一列
        new_row = row.shift(-1)
        new_row.iloc[-1] = pd.NA  # 最后一列补 NaN
        return new_row

def parse_time_column_safe(series):
    def convert(t):
        try:
            t = str(int(t)).zfill(6)[:6]
            return datetime.strptime(t, "%H%M%S").time()
        except Exception:
            return pd.NaT
    return series.apply(convert)

def deeplog_df_transfer(df, event_id_map):
    # 对每一行判断 Date 是否非法，如果非法就左移一行数据
    df = df.apply(left_shift_row_if_invalid_date, axis=1)

    # 解析 Date 列
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # 解析 Time 列（假设是 HHMMSS 格式的整数或字符串）
    df['Time'] = parse_time_column_safe(df['Time'])

    # 合并 Date 和 Time 为 datetime
    def safe_combine(row):
        if pd.notna(row['Date']) and pd.notna(row['Time']):
            return datetime.combine(row['Date'].date(), row['Time'])
        else:
            return pd.NaT

    df['datetime'] = df.apply(safe_combine, axis=1)

    # 保留有效字段
    df = df[['datetime', 'EventId']]

    # 映射 EventId
    df['EventId'] = df['EventId'].apply(lambda e: event_id_map.get(e, -1) if pd.notna(e) else -1)

    # 丢弃 datetime 为 NaT 的行
    df = df[df['datetime'].notna()]

    # 聚合为每秒事件列表
    deeplog_df = df.set_index('datetime').resample('1s').apply(_custom_resampler).dropna().reset_index()

    # 过滤掉空事件列表
    deeplog_df = deeplog_df[deeplog_df['EventId'].apply(lambda x: len(x) > 0)]

    return deeplog_df


def _custom_resampler(array_like):
    return list(array_like)


def deeplog_file_generator(filename, df):
    with open(filename, 'w+') as f:
        for event_id_list in df['EventId']:
            for event_id in event_id_list:
                f.write(str(event_id) + ' ')
            f.write('\n')


def preprocess(source_dir):
    ##########
    # Parser #
    ##########
    input_dir = './'
    # dir = "darpa_to_json_theia_uncompressed"
    # output_dir = './'+source_dir+'_result'
    log_format = '<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>'
    log_main = 'open_stack'
    tau = 0.5

    parser = spell.LogParser(
        indir=source_dir,
        outdir=source_dir,
        log_format=log_format,
        logmain=log_main,
        tau=tau,
    )

    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    for log_name in ['attack.log', 'normal_test.log','normal.log']:
        print(log_name)
        parser.parse(log_name)

    ##################
    # Transformation #
    ##################

    df = pd.read_csv(f'{source_dir}/normal.log_structured.csv')
    df_normal = pd.read_csv(f'{source_dir}/normal_test.log_structured.csv')
    df_abnormal = pd.read_csv(f'{source_dir}/attack.log_structured.csv')

    event_id_map = dict()
    for i, event_id in enumerate(df['EventId'].unique(), 1):
        event_id_map[event_id] = i

    logger.info(f'length of event_id_map: {len(event_id_map)}')

    #########
    # Train #
    #########
    deeplog_train = deeplog_df_transfer(df, event_id_map)
    deeplog_file_generator(source_dir+'/train', deeplog_train)

    # ###############
    # # Test Normal #
    # ###############
    deeplog_test_normal = deeplog_df_transfer(df_normal, event_id_map)
    deeplog_file_generator(source_dir+'/test_normal', deeplog_test_normal)

    # #################
    # # Test Abnormal #
    # #################
    deeplog_test_abnormal = deeplog_df_transfer(df_abnormal, event_id_map)
    # print(deeplog_test_abnormal)
    deeplog_file_generator(source_dir+'/test_abnormal', deeplog_test_abnormal)
    print("done")
    return len(event_id_map)