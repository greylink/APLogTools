# coding: utf-8

import os
import argparse
import subprocess
import configparser
import platform
import chardet
import Utils
from rules_config import LOG_FILE_SUFFIXES, OUTPUT_FILE_PREFIX, CONFIG_FILE# 导入规则配置

log_rules = {}  # 全局变量

def filter_log(input_file, rule_name, filter_keywords):
    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在。")
        return

    base_name, file_extension = os.path.splitext(os.path.basename(input_file))
    # 将与文件相关的变量转换为字符串
    output_directory = os.path.dirname(input_file.decode('utf-8')) if isinstance(input_file, bytes) else os.path.dirname(input_file)
    output_file = f'{OUTPUT_FILE_PREFIX}.{rule_name}.{base_name}{file_extension}'

    # 检查文件是否已经存在，如果存在则添加编号
    count = 0
    while os.path.exists(os.path.join(output_directory, output_file)):
        count += 1
        output_file = f'{OUTPUT_FILE_PREFIX}.{rule_name}.{base_name}.{count:02d}{file_extension}'

    output_file = os.path.join(output_directory, output_file)

    print(f"对 {input_file}，应用规则 {rule_name}")
    print(f"输出文件 {output_file}")

    count_matched_lines = 0

    encoding='utf-8'
    # 使用 chardet 检测文件编码,非常耗时!
    # with open(input_file, 'rb') as rawdata:
    #     result = chardet.detect(rawdata.read())
    #     encoding = result['encoding']

    with open(input_file, 'r', encoding=encoding, errors='ignore') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                if any(keyword in line for keyword in filter_keywords):
                    outfile.write(line)
                    count_matched_lines += 1
            except UnicodeDecodeError as e:
                print(f"解析 {input_file} 时遇到 UnicodeDecodeError: {e}")

    print(f"过滤完毕，共有 {count_matched_lines} 条")
    open_with_notepadplusplus(output_file)  # Open the filtered log file with Notepad++

def apply_rules(input_file, selected_rule=None):
    if selected_rule:
        if selected_rule in log_rules:
            rule = log_rules[selected_rule]
            filter_log(input_file, selected_rule, rule['keywords'])
        else:
            print(f"规则 '{selected_rule}' 不存在。")
            print(f"规则 '{log_rules}' 不存在。")
    else:
        print(f"应用所有过滤规则:")
        for rule_name, rule in log_rules.items():
            if rule_name != 'generic':
                filter_log(input_file, rule_name, rule['keywords']) 


def apply_rules_to_folder(folder, selected_rule=None):
    all_files = os.listdir(folder)
    # 过滤掉不是日志文件的项
    log_files = [file for file in all_files if not file.startswith(OUTPUT_FILE_PREFIX) and any(file.endswith(suffix) for suffix in LOG_FILE_SUFFIXES)]

    if not log_files:
        print(f"在 '{folder}' 中找不到日志文件。")
        return

    for log_file in log_files:
        input_file = os.path.join(folder, log_file)
        print(f"从 '{folder}' 中找 '{log_file}'")

        if selected_rule:
            apply_rules(input_file, selected_rule)
        else:
            apply_rules(input_file)


def open_with_notepadplusplus(file_path):

    hasNP, NPpath= Utils.get_notepadpp_info()

    if not hasNP:
        return

    notepadplusplus_path = r"C:\Program Files (x86)\Notepad++\notepad++.exe"

    # 检查 Notepad++ 是否存在
    if os.path.exists(NPpath):
        try:
            subprocess.Popen([NPpath, file_path])
        except Exception as e:
            print(f"Error opening file with Notepad++: {e}")
    else:
        print("Notepad++ not found.")

def main():
    parser = argparse.ArgumentParser(description="日志过滤工具,rules_config.py 可改输出文件的前缀，匹配文件的后缀，自定义规则关键字")
    parser.add_argument('input_file', help='日志文件名称或文件夹路径')
    parser.add_argument('rule_name', nargs='?', default=None, help='要应用的规则名称，默认为 None，表示应用所有规则')
    try:
        args = parser.parse_args()
    except SystemExit:
        print("错误：没有提供足够的参数。请至少提供一个输入文件名或文件夹路径。")
        return
    

    process_logs(args.input_file, args.rule_name)

def process_logs(input_file, rule_name_arg):

    # 使用 strip 方法删除可能存在的额外引号
    # rule_name_arg = rule_name_arg.strip("'") if rule_name_arg else None
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)


    # 获取规则和关键字
    for rule_name in config['log_rules']:
        rule_keywords = config.get('log_rules', rule_name).split('|')
        log_rules[rule_name] = {'keywords': rule_keywords}

    # 检查 rule_name_arg 是否存在于 log_rules 中
    if rule_name_arg not in log_rules:
        print(f"错误：规则 '{rule_name_arg}' 不存在于配置文件中。")
        return

    if os.path.isdir(input_file):
        apply_rules_to_folder(input_file, rule_name_arg)
    elif os.path.isfile(input_file):
        apply_rules(input_file, rule_name_arg)
    else:
        print(f"错误：输入 '{input_file}' 既不是文件也不是文件夹。")

if __name__ == '__main__':
    main()