#!/bin/bash

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install py2app

# 构建应用
python setup.py py2app 