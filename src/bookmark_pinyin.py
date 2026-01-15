#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import os
import copy
import re
import jieba
import logging
from logging.handlers import RotatingFileHandler
from pypinyin import lazy_pinyin
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 设置日志
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "bookmark_pinyin.log")

# 创建日志处理器，最大5MB，保留3个备份文件
logger = logging.getLogger('bookmark_pinyin')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 添加控制台输出
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# Chrome书签文件路径 - 支持环境变量配置
DEFAULT_BOOKMARK_PATH = '~/Library/Application Support/Google/Chrome/Default/Bookmarks'
BOOKMARK_PATH = os.path.expanduser(
    os.getenv('BOOKMARK_PATH', DEFAULT_BOOKMARK_PATH)
)

# 备份文件路径
BACKUP_PATH = os.path.expanduser(
    os.getenv('BACKUP_PATH', f'{BOOKMARK_PATH}.bak')
)

# 检查间隔（秒）
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '30'))


def read_bookmarks():
    """读取Chrome书签文件"""
    try:
        with open(BOOKMARK_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取书签文件出错: {e}")
        return None


def write_bookmarks(bookmarks):
    """写入Chrome书签文件"""
    try:
        # 先备份原文件
        if os.path.exists(BOOKMARK_PATH):
            with open(BOOKMARK_PATH, 'r', encoding='utf-8') as f_src:
                with open(BACKUP_PATH, 'w', encoding='utf-8') as f_dst:
                    f_dst.write(f_src.read())

        # 写入新的书签文件
        with open(BOOKMARK_PATH, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, ensure_ascii=False, indent=3)
        return True
    except Exception as e:
        logger.error(f"写入书签文件出错: {e}")
        return False


def process_name(name):
    """处理书签名称，添加分词后的拼音（仅处理含中文的书签）"""
    # 1. 移除 \r 及后续内容
    if '\r' in name:
        name = name.split('\r')[0].strip()

    # 2. 检查是否包含中文字符
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', name))

    if not has_chinese:
        # 没有中文，不处理
        logger.debug(f"无中文字符，跳过: '{name}'")
        return name

    # 3. 提取中文字符并生成拼音（关键：只对中文生成拼音）
    chinese_chars = ''.join(re.findall(r'[\u4e00-\u9fff]+', name))

    words = jieba.cut_for_search(chinese_chars)
    words_list = list(words)

    pinyin_results = []
    for word in words_list:
        if word.strip():
            word_pinyin = ''.join(lazy_pinyin(word))
            pinyin_results.append(word_pinyin)

    expected_pinyin = ''.join(pinyin_results)

    # 4. 去重逻辑：循环清理末尾的重复拼音
    clean_name = name
    max_iterations = 5

    for i in range(max_iterations):
        # 移除空格后检查（忽略大小写）
        test_name = clean_name.replace(' ', '').replace('\t', '').lower()
        expected_lower = expected_pinyin.lower()

        if expected_lower and test_name.endswith(expected_lower):
            # 从后往前移除 expected_pinyin 长度的字符
            chars_to_remove = len(expected_pinyin)
            temp = list(clean_name)
            removed = 0
            pos = len(temp) - 1

            while removed < chars_to_remove and pos >= 0:
                if temp[pos] not in [' ', '\t']:
                    temp[pos] = ''
                    removed += 1
                pos -= 1

            clean_name = ''.join(temp).strip()

            # 如果清理后没有中文了，说明过度清理，保留原名
            if not re.search(r'[\u4e00-\u9fff]', clean_name):
                logger.debug(f"清理后无中文，保留原名: '{name}'")
                clean_name = name
                break

            logger.debug(f"第{i+1}次清理: '{name}' → '{clean_name}'")
        else:
            # 不再有重复，退出
            break

    # 5. 返回结果
    return f"{clean_name} \r {expected_pinyin}"


def process_bookmark_node(node):
    """递归处理书签节点"""
    if 'type' in node:
        if node['type'] == 'url':
            # 处理URL类型的书签
            if 'name' in node and node['name'].strip():
                node['name'] = process_name(node['name'])
        elif node['type'] == 'folder':
            # 处理文件夹类型的书签
            if 'name' in node and node['name'].strip():
                node['name'] = process_name(node['name'])
            # 递归处理子节点
            if 'children' in node:
                for child in node['children']:
                    process_bookmark_node(child)


def process_all_bookmarks():
    """处理所有书签"""
    bookmarks = read_bookmarks()
    if not bookmarks:
        return False

    # 创建一个书签的副本用于处理
    modified_bookmarks = copy.deepcopy(bookmarks)

    # 处理书签栏节点
    if 'roots' in modified_bookmarks:
        for root_name, root_node in modified_bookmarks['roots'].items():
            process_bookmark_node(root_node)

    # 写入修改后的书签
    return write_bookmarks(modified_bookmarks)


def is_bookmarks_modified():
    """检查书签是否被还原（通过比较含中文的书签是否不包含拼音）"""
    bookmarks = read_bookmarks()
    if not bookmarks:
        return False

    # 检查函数 - 递归检查是否有含中文的书签不包含拼音
    def check_node(node):
        if 'type' in node:
            if node['type'] == 'url':
                # 检查URL类型的书签
                if 'name' in node and node['name'].strip():
                    name = node['name']
                    # 只检查包含中文的书签
                    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', name))
                    if has_chinese and '\r' not in name:
                        return True
            elif node['type'] == 'folder':
                # 检查文件夹类型的书签
                if 'name' in node and node['name'].strip():
                    name = node['name']
                    # 只检查包含中文的书签
                    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', name))
                    if has_chinese and '\r' not in name:
                        return True
                # 递归检查子节点
                if 'children' in node:
                    for child in node['children']:
                        if check_node(child):
                            return True
        return False

    # 检查所有根节点
    if 'roots' in bookmarks:
        for root_name, root_node in bookmarks['roots'].items():
            if check_node(root_node):
                return True

    return False


def main():
    """主函数"""
    logger.info(f"开始处理Chrome书签，添加分词后的拼音...")
    logger.info(f"书签路径: {BOOKMARK_PATH}")
    logger.info(f"备份路径: {BACKUP_PATH}")
    logger.info(f"检查间隔: {CHECK_INTERVAL}秒")

    # 首次处理所有书签
    if process_all_bookmarks():
        logger.info("初始书签处理完成")
    else:
        logger.error("初始书签处理失败")
        return

    # 定期检查书签是否被还原
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            logger.info("检查书签是否被还原...")

            if is_bookmarks_modified():
                logger.info("检测到书签被还原，重新处理...")
                process_all_bookmarks()
                logger.info("书签重新处理完成")
            else:
                logger.info("书签未被还原，继续监控...")
        except KeyboardInterrupt:
            logger.info("程序被用户中断")
            break
        except Exception as e:
            logger.error(f"发生错误: {e}")
            time.sleep(10)  # 发生错误后等待一段时间再继续


if __name__ == "__main__":
    main()
