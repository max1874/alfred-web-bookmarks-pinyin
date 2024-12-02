import os
import time

# 文件路径
file_path = "/Users/ritsu/Library/Application Support/Google/Chrome/Default/Bookmarks"

# 获取最后修改时间
last_modified_time = os.path.getmtime(file_path)

# 转换为可读格式
readable_time = time.ctime(last_modified_time)