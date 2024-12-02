import logging
from pathlib import Path
from bookmarks_pinyin import BookmarkProcessor, logger

def main():
    """主程序入口"""
    # 配置文件路径
    bookmark_path = '~/Library/Application Support/Google/Chrome/Default/Bookmarks'
    update_time_file = 'update_time.txt'
    
    # 创建处理器实例
    processor = BookmarkProcessor(bookmark_path, update_time_file)
    
    try:
        # 检查是否需要更新
        if not processor.should_update():
            logger.info("Bookmarks are up to date")
            return
            
        # 读取书签内容
        content = processor.read_bookmarks()
        if content is None:
            return
            
        # 处理书签
        processor.process_bookmarks(content)
        
        # 写回文件
        if processor.write_bookmarks(content):
            # 更新时间戳
            current_time = processor.get_file_update_time()
            if current_time:
                processor.write_update_time(current_time)
                logger.info("Successfully processed bookmarks")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()