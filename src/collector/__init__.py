"""
数据收集器模块
负责收集系统资源使用情况和系统日志
"""

from .system_collector import SystemCollector
from .log_collector import LogCollector

__all__ = ['SystemCollector', 'LogCollector'] 