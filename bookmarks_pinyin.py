import json
import jieba
import os
from typing import Dict, Any, Optional
from pypinyin import lazy_pinyin
from pathlib import Path
import logging
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
jieba.setLogLevel(jieba.logging.INFO)

@dataclass
class BookmarkProcessor:
    file_path: Path
    update_time_file: Path
    
    def __post_init__(self):
        self.file_path = Path(self.file_path).expanduser()
        self.update_time_file = Path(self.update_time_file)
    
    def process_bookmark_name(self, name: str) -> str:
        """处理单个书签名称，返回处理后的结果"""
        # 删除 \r 及其后面的内容
        name = name.split('\r')[0]
        
        # 分词并转换为拼音
        words = jieba.cut_for_search(name)
        words_with_space = ' '.join(words)
        pinyin_list = lazy_pinyin(words_with_space)
        
        # 去重并保持原始顺序
        unique_pinyin = list(dict.fromkeys(pinyin_list))
        
        # 找到第一个拼音在原文中的位置
        if unique_pinyin:
            first_pinyin = unique_pinyin[0]
            first_pos = name.find(first_pinyin, 1)  # 从位置1开始搜索
            if first_pos != -1:
                name = name[:first_pos]
        
        return f"{name}\r{''.join(unique_pinyin)}"
    
    def process_bookmarks(self, obj: Dict[str, Any]) -> None:
        """递归处理书签对象"""
        if isinstance(obj, dict):
            if "name" in obj and isinstance(obj["name"], str):
                obj["name"] = self.process_bookmark_name(obj["name"])
            for value in obj.values():
                self.process_bookmarks(value)
        elif isinstance(obj, list):
            for item in obj:
                self.process_bookmarks(item)

    def get_file_update_time(self) -> Optional[float]:
        """获取文件最后修改时间"""
        try:
            return self.file_path.stat().st_mtime if self.file_path.exists() else None
        except OSError as e:
            logger.error(f"Error getting file update time: {e}")
            return None
    
    def read_last_update_time(self) -> Optional[float]:
        """读取上次更新时间"""
        try:
            return float(self.update_time_file.read_text()) if self.update_time_file.exists() else None
        except (ValueError, OSError) as e:
            logger.error(f"Error reading last update time: {e}")
            return None
    
    def write_update_time(self, update_time: float) -> None:
        """写入更新时间"""
        try:
            self.update_time_file.write_text(str(update_time))
        except OSError as e:
            logger.error(f"Error writing update time: {e}")
            
    def read_bookmarks(self) -> Optional[Dict]:
        """读取书签文件内容"""
        try:
            return json.loads(self.file_path.read_bytes().decode('utf-8'))
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Error reading bookmarks file: {e}")
            return None
            
    def write_bookmarks(self, content: Dict) -> bool:
        """写入书签文件内容"""
        try:
            self.file_path.write_bytes(
                json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
            )
            return True
        except OSError as e:
            logger.error(f"Error writing bookmarks file: {e}")
            return False

    def should_update(self) -> bool:
        """检查是否需要更新书签"""
        current_time = self.get_file_update_time()
        last_update = self.read_last_update_time()
        
        if current_time is None:
            logger.error("Cannot access bookmark file")
            return False
            
        return last_update is None or current_time != last_update