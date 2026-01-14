import logging
from pathlib import Path

def setup_logger(config):
    logger = logging.getLogger('BookmarksSync')
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    log_path = Path(config.get('log_file', 'bookmarks_sync.log'))
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 