# alfred-web-bookmarks-pinyin

为 Alfred 的书签搜索添加中文拼音支持的工具。通过结合 jieba 分词和拼音转换，显著提升中文书签的搜索体验。

**示例**：`明日方舟` → `明日方舟\rmrfz`，现在可以通过"方舟"、"fz"、"mrfz"等方式搜索到。

## 功能特点

- 支持中文拼音搜索
- 使用 jieba 分词提高搜索准确度
- 双运行模式：CLI + GUI 菜单栏应用
- 增量更新，避免重复处理
- 完善的日志系统
- 自动定时更新书签索引

## 环境要求

- macOS 操作系统
- Python 3.6+
- Google Chrome 浏览器
- Alfred (with Powerpack)

## 使用方式

### 方式一：菜单栏应用（推荐）

1. 克隆项目到本地
   ```bash
   git clone https://github.com/Kudoryafuka3/alfred-web-bookmarks-pinyin.git
   cd alfred-web-bookmarks-pinyin
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 运行菜单栏应用
   ```bash
   python app.py
   ```

4. （可选）编译为独立应用
   ```bash
   bash build.sh
   ```
   编译完成后，应用会在 `dist/` 目录下生成。

**菜单栏应用功能**：
- 手动同步书签
- 开启/关闭自动同步（默认 5 分钟一次）
- 实时查看同步状态

### 方式二：LaunchAgent 后台任务

1. 克隆项目并安装依赖（同上）

2. 配置启动脚本权限
   ```bash
   chmod +x ./execute_python_script.sh
   ```

3. 修改 `execute_python_script.sh` 和 `com.mycompany.myscript.plist` 中的脚本路径为实际路径

4. 复制 plist 文件到 LaunchAgents
   ```bash
   cp com.mycompany.myscript.plist ~/Library/LaunchAgents/
   ```

5. 加载定时任务
   ```bash
   launchctl load ~/Library/LaunchAgents/com.mycompany.myscript.plist
   ```

6. 验证任务是否加载成功
   ```bash
   launchctl list | grep com.mycompany.myscript
   ```

### 方式三：命令行直接运行

```bash
python main.py
```

## 配置说明

编辑 `config.py` 可以修改以下配置：

- `bookmarks.chrome`：Chrome 书签文件路径（默认：`~/Library/Application Support/Google/Chrome/Default/Bookmarks`）
- `auto_sync.enabled`：是否启用自动同步（默认：`False`）
- `auto_sync.interval`：自动同步间隔秒数（默认：`300`）
- `log_file`：日志文件路径（默认：`bookmarks_sync.log`）
- `update_time_file`：时间戳文件路径（默认：`update_time.txt`）

## 技术实现

### 实现原理

工具使用 jieba 分词的搜索模式对中文书签进行分词处理，然后将分词结果转换为拼音。这样即使搜索词与书签名称不完全匹配，也能找到相关结果。例如，搜索"fz"或"方舟"都能找到"明日方舟"的书签。

### 核心流程

```
读取 Chrome 书签 JSON
    ↓
jieba 分词（搜索模式）
    ↓
pypinyin 转拼音首字母
    ↓
拼音去重
    ↓
重写书签名称为 "原名\r拼音串"
    ↓
写回书签文件
```

### 依赖包

- `pypinyin`：中文转拼音
- `jieba`：中文分词
- `rumps`：macOS 菜单栏应用框架
- `pyyaml`：配置文件解析
- `py2app`：打包为 macOS 应用

## 常见问题

### 每次打开都看到通知 "xxx.sh 已在后台运行"

执行以下命令关闭通知：
```bash
sudo sfltool resetbtm
```

参考链接：[后台项目已添加的通知如何关闭](https://discussionschinese.apple.com/thread/254470532)

### 停用定时任务

如需停用定时更新服务，执行：
```bash
launchctl unload ~/Library/LaunchAgents/com.mycompany.myscript.plist
```

### 查看日志

```bash
tail -f bookmarks_sync.log
```

### 支持其他浏览器吗？

目前仅支持 Chrome/Chromium 系浏览器。如需支持其他浏览器，可以修改 `config.py` 中的书签文件路径。

## 项目结构

```
alfred-web-bookmarks-pinyin/
├── bookmarks_pinyin.py          # 核心处理模块
├── main.py                       # CLI 命令行入口
├── app.py                        # GUI 菜单栏应用
├── config.py                     # 配置管理
├── logger.py                     # 日志模块
├── requirements.txt              # Python 依赖
├── setup.py                      # py2app 打包配置
├── build.sh                      # 编译脚本
├── execute_python_script.sh      # LaunchAgent 执行脚本
├── com.mycompany.myscript.plist  # LaunchAgent 配置
└── last_update.py                # 时间戳获取工具
```

## 故障排除

1. 确保书签文件路径正确
2. 检查 Python 环境和依赖包安装状态
3. 验证定时任务是否正常运行
4. 查看日志文件排查问题

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。提交时请：
- 清晰描述问题或改进建议
- 提供必要的代码示例
- 遵循现有的代码风格

## 许可证

MIT License
