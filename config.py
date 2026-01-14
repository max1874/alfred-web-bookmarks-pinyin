from typing import Any
import yaml

class Config:
    def __init__(self):
        self.settings = {
            'log_file': 'bookmarks_sync.log',
            'auto_sync.enabled': False,
            'auto_sync.interval': 300,
            'bookmarks.chrome': '~/Library/Application Support/Google/Chrome/Default/Bookmarks',
            'update_time_file': 'update_time.txt'
        }

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value 