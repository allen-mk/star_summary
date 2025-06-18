#!/usr/bin/env python3
"""
日志配置工具
为CLI工具提供统一的日志配置功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import colorama
from colorama import Fore, Style


def setup_logging(
    verbose: bool = False,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        verbose: 是否启用详细输出
        log_file: 日志文件路径，默认为 'star_summary.log'
        console_output: 是否输出到控制台
    
    Returns:
        配置好的logger对象
    """
    # 初始化colorama（用于彩色输出）
    colorama.init(autoreset=True)
    
    # 设置日志级别
    level = logging.DEBUG if verbose else logging.INFO
    
    # 创建logger
    logger = logging.getLogger('star_summary')
    logger.setLevel(level)
    
    # 清除现有的handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # 添加文件handler
    if log_file is None:
        log_file = 'star_summary.log'
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # 添加控制台handler
    if console_output:
        console_handler = ColoredConsoleHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    return logger


class ColoredConsoleHandler(logging.StreamHandler):
    """带颜色的控制台日志处理器"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def emit(self, record):
        try:
            msg = self.format(record)
            color = self.COLORS.get(record.levelname, '')
            
            # 为不同级别的日志添加颜色
            if color:
                msg = f"{color}{msg}{Style.RESET_ALL}"
            
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def get_logger(name: str = 'star_summary') -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称
    
    Returns:
        logger实例
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, exc_info: bool = True):
    """
    记录异常信息的装饰器
    
    Args:
        logger: logger实例
        exc_info: 是否包含异常堆栈信息
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}", exc_info=exc_info)
                raise
        return wrapper
    return decorator


class ProgressLogger:
    """带进度的日志记录器"""
    
    def __init__(self, logger: logging.Logger, total_steps: int):
        self.logger = logger
        self.total_steps = total_steps
        self.current_step = 0
    
    def step(self, message: str = ""):
        """记录进度步骤"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        
        if message:
            self.logger.info(f"[{progress:.1f}%] {message}")
        else:
            self.logger.info(f"Progress: {progress:.1f}%")
    
    def complete(self, message: str = "完成"):
        """标记完成"""
        self.logger.info(f"✅ {message}")


# 预定义的日志消息
class LogMessages:
    """常用日志消息"""
    
    @staticmethod
    def start_task(task_name: str) -> str:
        return f"🚀 开始执行: {task_name}"
    
    @staticmethod
    def complete_task(task_name: str) -> str:
        return f"✅ 完成任务: {task_name}"
    
    @staticmethod
    def error_task(task_name: str, error: str) -> str:
        return f"❌ 任务失败: {task_name} - {error}"
    
    @staticmethod
    def fetching_repos(count: int) -> str:
        return f"📡 正在获取 {count} 个星标项目..."
    
    @staticmethod
    def classifying_repos(count: int) -> str:
        return f"🏷️ 正在分类 {count} 个项目..."
    
    @staticmethod
    def generating_docs(format_type: str) -> str:
        return f"📝 正在生成 {format_type} 格式文档..."
    
    @staticmethod
    def saving_output(path: str) -> str:
        return f"💾 正在保存到: {path}"
