import rumps
import threading
from pathlib import Path
from config import Config
from logger import setup_logger
from bookmarks_pinyin import BookmarkProcessor

class BookmarksSyncApp(rumps.App):
    def __init__(self):
        print("Starting BookmarksSyncApp...")
        super().__init__("📚")
        
        try:
            # 初始化配置和日志
            print("Initializing config and logger...")
            self.config = Config()
            self.logger = setup_logger(self.config)
            
            # 初始化处理器
            print("Initializing bookmark processor...")
            self.processor = BookmarkProcessor(
                bookmark_path=self.config.get('bookmarks.chrome'),
                update_time_file=self.config.get('update_time_file'),
                logger=self.logger
            )
            
            # 设置菜单项
            print("Setting up menu items...")
            self.sync_button = rumps.MenuItem("同步书签", callback=self.sync_bookmarks)
            self.auto_sync = rumps.MenuItem("自动同步", callback=self.toggle_auto_sync)
            self.status_text = rumps.MenuItem("状态: 空闲")
            
            # 添加菜单项
            self.menu = [
                self.sync_button,
                None,  # 分割线
                self.auto_sync,
                self.status_text,
                None,  # 分割线
            ]
            
            # 初始化自动同步定时器
            self.sync_timer = None
            self.load_auto_sync_state()
            print("Initialization complete!")
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    @rumps.clicked("同步书签")
    def sync_bookmarks(self, _):
        """手动同步书签"""
        def sync():
            self.status_text.title = "状态: 同步中..."
            self.sync_button.set_callback(None)  # 禁用同步按钮
            
            try:
                if not self.processor.should_update():
                    self.status_text.title = "状态: 书签已是最新"
                    return
                    
                content = self.processor.read_bookmarks()
                if content is None:
                    self.status_text.title = "状态: 读取书签失败"
                    return
                    
                self.processor.process_bookmarks(content)
                
                if self.processor.write_bookmarks(content):
                    current_time = self.processor.get_file_update_time()
                    if current_time:
                        self.processor.write_update_time(current_time)
                        self.status_text.title = "状态: 同步成功"
                else:
                    self.status_text.title = "状态: 写入失败"
                    
            except Exception as e:
                self.logger.error(f"同步失败: {e}", exc_info=True)
                self.status_text.title = f"状态: 同步失败 - {str(e)}"
            finally:
                self.sync_button.set_callback(self.sync_bookmarks)  # 重新启用同步按钮
        
        # 在后台线程中执行同步
        threading.Thread(target=sync).start()

    @rumps.clicked("自动同步")
    def toggle_auto_sync(self, sender):
        """切换自动同步状态"""
        sender.state = not sender.state
        self.config.set('auto_sync.enabled', sender.state)
        
        if sender.state:
            self.start_auto_sync()
        else:
            self.stop_auto_sync()

    def start_auto_sync(self):
        """启动自动同步"""
        interval = self.config.get('auto_sync.interval', 300)  # 默认5分钟
        self.sync_timer = rumps.Timer(self.sync_bookmarks, interval)
        self.sync_timer.start()
        self.logger.info(f"自动同步已启动，间隔: {interval}秒")

    def stop_auto_sync(self):
        """停止自动同步"""
        if self.sync_timer:
            self.sync_timer.stop()
            self.sync_timer = None
        self.logger.info("自动同步已停止")

    def load_auto_sync_state(self):
        """加载自动同步状态"""
        if self.config.get('auto_sync.enabled', False):
            self.auto_sync.state = True
            self.start_auto_sync()

def main():
    try:
        print("Starting main...")
        app = BookmarksSyncApp()
        print("Running app...")
        app.run(debug=True)
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main() 