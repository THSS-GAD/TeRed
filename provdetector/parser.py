import json
import os
import shutil


# 单文件处理图数据到日志形式
def json_to_tuple(input_file: str, output_file: str):
    with open(input_file, 'r') as json_file:
        data = json.load(json_file)
    with open(output_file, 'w') as output_file:
        for link in data['links']:
            ts = link['ts'].replace(':', '')
            ts = ts.replace('.', '')
            ts = str(int(ts))
            syscall = link['syscall']
            success = link['success']
            source_type = link['source_type']
            target_type = link['target_type']
            source = link['source']
            target = link['target']
            if success:
                output_file.write(f"{source}\t{source_type}\t{target}\t{target_type}\t{syscall}\t{ts}\n")


# 文件夹处理图数据到日志形式
def folder_json_to_tuple(input_folder: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(input_folder):
        if not filename.endswith('.json'):
            continue
        input_filepath = os.path.join(input_folder, filename)
        if os.path.isfile(input_filepath):
            output_filepath = os.path.join(output_folder, filename)
            json_to_tuple(input_filepath, output_filepath.replace('.json', '.txt'))


# 对数据包特殊处理图数据到日志形式
def package_json_to_tuple():
    in_path = '../../data/reduced_data'
    out_path = 'data/reduced_data'
    for folders in os.listdir(in_path):
        for folder in os.listdir(in_path+'/'+folders):
            folder_json_to_tuple(in_path+'/'+folders + '/' + folder, out_path+'/'+folders + '/' + folder)


# 切分训练数据与验证数据
def split_by_folder(normal_dataset: str, attack_dataset: str, output_folder):
    # 获取normal_dataset和attack_dataset文件列表
    normal_files = os.listdir(normal_dataset)
    attack_files = os.listdir(attack_dataset)

    # 创建输出文件夹
    for i in range(5):
        folder_path = os.path.join(output_folder, f'folder_{i + 1}')
        if not os.path.exists(os.path.join(folder_path, 'train_dataset')):
            os.makedirs(os.path.join(folder_path, 'train_dataset'))

        if not os.path.exists(os.path.join(folder_path, 'test_dataset')):
            os.makedirs(os.path.join(folder_path, 'test_dataset'))

        # 计算每组应包含的normal_dataset文件数
        files_per_group = len(normal_files) // 5

        # 计算当前组的起始和结束索引
        start_index = i * files_per_group
        end_index = (i + 1) * files_per_group

        for file in normal_files[:start_index]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'train_dataset', file))
        for file in normal_files[end_index:]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'train_dataset', file))

        # 移动normal_dataset的文件到对应文件夹
        for file in normal_files[start_index:end_index]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'test_dataset', file))

        # 移动attack_dataset的所有文件到对应文件夹
        for file in attack_files:
            shutil.copy(os.path.join(attack_dataset, file),
                        os.path.join(folder_path, 'test_dataset', file))


def split_by_onefolder(input_folder: str, output_folder: str):
    folder_path = input_folder  # 替换为你的文件夹路径
    file_list = os.listdir(folder_path)

    normal_files = [file for file in file_list if 'normal' in file]
    attack_files = [file for file in file_list if 'attack' in file]

    normal_dataset = input_folder
    attack_dataset = input_folder

    # 创建输出文件夹
    for i in range(5):
        folder_path = os.path.join(output_folder, f'folder_{i + 1}')
        if not os.path.exists(os.path.join(folder_path, 'train_dataset')):
            os.makedirs(os.path.join(folder_path, 'train_dataset'))

        if not os.path.exists(os.path.join(folder_path, 'test_dataset')):
            os.makedirs(os.path.join(folder_path, 'test_dataset'))

        # 计算每组应包含的normal_dataset文件数
        files_per_group = len(normal_files) // 5

        # 计算当前组的起始和结束索引
        start_index = i * files_per_group
        end_index = (i + 1) * files_per_group

        for file in normal_files[:start_index]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'train_dataset', file))
        for file in normal_files[end_index:]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'train_dataset', file))

        # 移动normal_dataset的文件到对应文件夹
        for file in normal_files[start_index:end_index]:
            shutil.copy(os.path.join(normal_dataset, file),
                        os.path.join(folder_path, 'test_dataset', file))

        # 移动attack_dataset的所有文件到对应文件夹
        for file in attack_files:
            shutil.copy(os.path.join(attack_dataset, file),
                        os.path.join(folder_path, 'test_dataset', file))

def split_package():

    method_list = ['CPR', 'FDPR', 'LogApprox', 'LogGC', 'NodeMerge', 'Origin', 'PCAR', 'SDPR']
    input_folder = 'data/reduced_data'
    output_folder = 'data/reduced_data_made'
    onefolder_list = ['cve-2014-6271-multi', 'cve-2016-4971_all', 'cve-2019-9193']
    doublefolder_list = [['theia_normal', 'theia_attack'], ['trace_normal', 'trace_attack']]

    for method in method_list:
        for folder in onefolder_list:
            split_by_onefolder(f'{input_folder}/{method}/{folder}', f'{output_folder}/{method}/{folder}')
        for folder in doublefolder_list:
            split_by_folder(f'{input_folder}/{method}/{folder[0]}', f'{input_folder}/{method}/{folder[1]}',
                            f'{output_folder}/{method}/{folder[0][:5]}')




if __name__ == '__main__':
    # json_to_tuple('../../data/reduced_data/CPR/theia_normal/darpa_small_file_2_normal.json', 'data_test.txt')
    # folder_json_to_tuple('../../data/scenes/reduced/Original/theia/darpa_to_json_theia_attack',
    #                      'data/scenes/reduced/Original/theia/darpa_to_json_theia_attack')
    #package_json_to_tuple()
    split_package()
