# alfred-web-bookmarks-pinyin

为 Alfred 的书签搜索添加中文拼音支持的工具。通过结合 jieba 分词和拼音转换，显著提升中文书签的搜索体验。

**示例**：`明日方舟` → `明日方舟 \r mingrifangzhou`，现在可以通过"方舟"、"fangzhou"、"mrfz"等方式搜索到。

## 功能特点

- 支持中文拼音搜索
- 使用 jieba 分词提高搜索准确度
- 智能监控：每30秒自动检查书签是否被还原，自动重新处理
- 自动备份：每次修改前自动备份原书签文件
- 日志轮转：自动管理日志文件（最大5MB，保留3个备份）
- 环境变量配置：支持自定义书签路径和检查间隔
- 简单的服务管理：start/stop/restart/status

## 环境要求

- macOS 操作系统
- Python 3.6+
- Google Chrome 浏览器（或其他 Chromium 系浏览器）
- Alfred (with Powerpack)

## 安装使用

### 1. 克隆项目

```bash
git clone https://github.com/max1874/alfred-web-bookmarks-pinyin.git
cd alfred-web-bookmarks-pinyin
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置（可选）

项目会自动读取项目根目录的 `.env` 文件。如需自定义配置，可以创建 `.env` 文件：

```bash
# 复制示例配置
cp examples/.env.example .env

# 编辑配置
vim .env
```

**默认配置**（无需 .env 文件也能运行）：
- Chrome 书签路径：`~/Library/Application Support/Google/Chrome/Default/Bookmarks`
- 检查间隔：30 秒

### 4. 启动服务

#### 方式一：使用服务管理脚本（推荐）

```bash
# 启动服务
python src/run_as_service.py start

# 查看服务状态
python src/run_as_service.py status

# 重启服务
python src/run_as_service.py restart

# 停止服务
python src/run_as_service.py stop
```

服务启动后会在后台持续运行，日志输出到 `bookmark_pinyin.log` 文件。

#### 方式二：直接运行

```bash
python src/bookmark_pinyin.py
```

直接运行时，按 `Ctrl+C` 可停止程序。

## 配置说明

项目使用 `.env` 文件进行配置。默认配置已经可以直接使用，无需额外设置。

### 自定义配置

如需修改配置（如使用 Edge 或 Brave 浏览器），创建 `.env` 文件：

```bash
# 复制示例配置
cp examples/.env.example .env

# 编辑 .env 文件
# Chrome（默认）
BOOKMARK_PATH=~/Library/Application Support/Google/Chrome/Default/Bookmarks

# Edge
BOOKMARK_PATH=~/Library/Application Support/Microsoft Edge/Default/Bookmarks

# Brave
BOOKMARK_PATH=~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Bookmarks

# 其他配置
BACKUP_PATH=~/Library/Application Support/Google/Chrome/Default/Bookmarks.bak
CHECK_INTERVAL=30
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `BOOKMARK_PATH` | 浏览器书签文件路径 | Chrome 默认路径 |
| `BACKUP_PATH` | 备份文件路径 | `{BOOKMARK_PATH}.bak` |
| `CHECK_INTERVAL` | 检查间隔（秒） | `30` |

## 技术实现

### 工作原理

1. **分词处理**：使用 jieba 的搜索模式对书签名称进行分词
2. **拼音转换**：使用 pypinyin 将分词结果转换为拼音
3. **格式化**：将原名称和拼音组合为 `原名称 \r 拼音` 格式
4. **智能监控**：定期检查书签是否被浏览器还原，自动重新处理

### 处理流程

```
读取 Chrome 书签 JSON
    ↓
jieba 分词（搜索模式）
    ↓
pypinyin 转拼音
    ↓
格式化为 "原名 \r 拼音"
    ↓
备份原文件
    ↓
写回书签文件
    ↓
每30秒检查是否被还原
```

### 依赖包

- `jieba`：中文分词
- `pypinyin`：中文转拼音
- `python-dotenv`：.env 文件配置加载

## 项目结构

```
alfred-web-bookmarks-pinyin/
├── src/
│   ├── bookmark_pinyin.py      # 主程序脚本，负责处理书签和监控
│   └── run_as_service.py       # 服务管理脚本，用于后台运行管理
├── examples/
│   └── .env.example            # 配置文件示例
├── README.md                    # 项目文档
├── requirements.txt             # 项目依赖
├── LICENSE                      # 许可证
└── bookmark_pinyin.log          # 运行日志（自动生成）
```

## 常见问题

### 支持其他浏览器吗？

支持所有基于 Chromium 的浏览器（Chrome、Edge、Brave等）。只需通过 `BOOKMARK_PATH` 环境变量指定正确的书签文件路径即可。

### 如何查看日志？

```bash
# 查看最新日志
tail -f bookmark_pinyin.log

# 查看服务状态（包含最近5条日志）
python src/run_as_service.py status
```

### 书签会丢失吗？

不会。程序每次修改书签前都会自动备份到 `.bak` 文件。如果出现问题，可以从备份文件恢复。

### 如何开机自启动？

可以使用 macOS 的 LaunchAgent：

1. 创建 `~/Library/LaunchAgents/com.bookmark.pinyin.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bookmark.pinyin</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/python</string>
        <string>/path/to/alfred-web-bookmarks-pinyin/src/bookmark_pinyin.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

2. 加载服务：

```bash
launchctl load ~/Library/LaunchAgents/com.bookmark.pinyin.plist
```

## 故障排除

1. **服务无法启动**：检查 Python 环境和依赖包是否正确安装
2. **书签未更新**：查看日志文件确认是否有错误信息
3. **权限问题**：确保对书签文件有读写权限

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。提交时请：
- 清晰描述问题或改进建议
- 提供必要的代码示例
- 遵循现有的代码风格

## 许可证

MIT License
