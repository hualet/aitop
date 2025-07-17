"""
AITop - 智能系统监控工具

一个结合了传统top命令实时性和AI分析智能性的系统监控工具。
它提供类似top的命令行界面来实时监控系统进程，并在收集一段时间数据后
生成智能化的HTML5分析报告。
"""

__version__ = "1.0.0"
__author__ = "AITop Team"
__email__ = "team@aitop.dev"
__license__ = "MIT"


def main():
    """主入口函数"""
    try:
        from .cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所需依赖: pip install psutil")
        return 1
    except Exception as e:
        print(f"运行时错误: {e}")
        return 1
    
    return 0


__all__ = ["main"]
