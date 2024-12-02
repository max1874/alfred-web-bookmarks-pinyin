# alfred-web-bookmarks-pinyin

为 Alfred 的书签搜索添加中文拼音支持的工具。通过结合 jieba 分词和拼音转换，显著提升中文书签的搜索体验。

## 功能特点

- 支持中文拼音搜索
- 使用 jieba 分词提高搜索准确度
- 自动定时更新书签索引
- 支持 Google Chrome 书签

## 实现原理

工具使用 jieba 分词的搜索模式对中文书签进行分词处理，然后将分词结果转换为拼音。这样即使搜索词与书签名称不完全匹配，也能找到相关结果。例如，搜索"fz"或"方舟"都能找到"明日方舟"的书签。

## 环境要求

- macOS 操作系统
- Python 3.6+
- Google Chrome 浏览器
- Alfred (with Powerpack)

## 依赖包

- pypinyin：中文转拼音
- jieba：中文分词

## 安装步骤

1. 克隆仓库到本地
   ```bash
   git clone [repository-url]
   cd alfred-web-bookmarks-pinyin
   ```

2. 安装依赖包
   ```bash
   pip install pypinyin jieba
   ```

3. 配置启动脚本权限
   ```bash
   chmod +x ./execute_python_script.sh
   ```

4. 设置定时任务
   - 复制定时任务配置文件：
     ```bash
     cp com.mycompany.myscript.plist ~/Library/LaunchAgents/
     ```
   - 加载定时任务：
     ```bash
     launchctl load ~/Library/LaunchAgents/com.mycompany.myscript.plist
     ```
   - 验证任务加载状态：
     ```bash
     launchctl list | grep com.mycompany.myscript
     ```

## 配置说明

### 书签文件路径
默认支持的 Chrome 书签路径：
```
~/Library/Application Support/Google/Chrome/Default/Bookmarks
```

### 定时任务配置
定时任务配置文件 `com.mycompany.myscript.plist` 需要根据实际情况修改：
1. 修改脚本路径
2. 调整运行间隔时间
3. 配置环境变量（如需要）

## 常见问题

### 后台运行通知
问题：每次运行都会收到 "xxx.sh 已在后台运行" 的通知。
解决方案：执行以下命令关闭通知：
```bash
sudo sfltool resetbtm
```

### 停用服务
如需停用定时更新服务，执行：
```bash
launchctl unload ~/Library/LaunchAgents/com.mycompany.myscript.plist
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

[许可证类型]

## 更多信息

详细的技术实现说明请参考[博客文章](https://kudoryafuka3.github.io/2023/08/13/%E8%AE%A9-Alfred-%E8%87%AA%E5%B8%A6%E7%9A%84%E4%B9%A6%E7%AD%BE%E6%90%9C%E7%B4%A2%E6%94%AF%E6%8C%81%E6%8B%BC%E9%9F%B3%E5%8A%9F%E8%83%BD/)。
