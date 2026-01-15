#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time

def start_service():
    """启动书签监控服务"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # 项目根目录
    script_path = os.path.join(script_dir, "bookmark_pinyin.py")

    # 检查主程序是否存在
    if not os.path.exists(script_path):
        print(f"错误: 找不到主程序 '{script_path}'")
        return False

    # 检查是否已经有进程在运行
    if is_running():
        print("服务已经在运行中")
        return True

    # 日志文件路径（现在主要用于状态显示）
    log_path = os.path.join(script_dir, "bookmark_pinyin.log")

    # 检测并使用虚拟环境的 Python
    venv_python = os.path.join(project_root, '.venv', 'bin', 'python')

    if os.path.exists(venv_python):
        python_cmd = venv_python
        print(f"使用虚拟环境: {venv_python}")
    else:
        python_cmd = sys.executable
        print(f"虚拟环境未找到，使用当前 Python: {python_cmd}")

    cmd = f"nohup {python_cmd} -u {script_path} > /dev/null 2>&1 &"

    try:
        subprocess.run(cmd, shell=True, check=True)
        time.sleep(1)  # 等待进程启动

        if is_running():
            print(f"服务已成功启动")
            print(f"日志文件: {log_path}")
            return True
        else:
            print("启动服务失败")
            return False
    except Exception as e:
        print(f"启动服务时出错: {e}")
        return False

def stop_service():
    """停止书签监控服务"""
    pid = get_pid()
    if pid:
        try:
            os.kill(int(pid), 15)  # 发送SIGTERM信号
            print(f"服务(PID:{pid})已停止")
            return True
        except Exception as e:
            print(f"停止服务时出错: {e}")
            return False
    else:
        print("没有找到运行中的服务")
        return False

def is_running():
    """检查服务是否在运行"""
    return get_pid() is not None

def get_pid():
    """获取运行中的进程PID"""
    try:
        cmd = "ps aux | grep '[b]ookmark_pinyin.py' | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True, text=True)
        if result.strip():
            return result.strip()
        return None
    except:
        return None

def show_status():
    """显示服务状态"""
    pid = get_pid()
    if pid:
        print(f"服务正在运行 (PID: {pid})")

        # 显示运行时间
        cmd = f"ps -o etime= -p {pid}"
        try:
            runtime = subprocess.check_output(cmd, shell=True, text=True).strip()
            print(f"已运行时间: {runtime}")
        except:
            pass

        # 显示日志文件最后几行
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, "bookmark_pinyin.log")
        if os.path.exists(log_path):
            print("\n最近日志:")
            try:
                cmd = f"tail -n 5 {log_path}"
                log_content = subprocess.check_output(cmd, shell=True, text=True)
                print(log_content)
            except:
                pass
    else:
        print("服务未运行")

def print_usage():
    """打印使用帮助"""
    print("使用方法:")
    print("  python run_as_service.py start   - 启动服务")
    print("  python run_as_service.py stop    - 停止服务")
    print("  python run_as_service.py restart - 重启服务")
    print("  python run_as_service.py status  - 查看服务状态")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["start", "stop", "restart", "status"]:
        print_usage()
        sys.exit(1)

    action = sys.argv[1]

    if action == "start":
        start_service()
    elif action == "stop":
        stop_service()
    elif action == "restart":
        stop_service()
        time.sleep(2)
        start_service()
    elif action == "status":
        show_status()
