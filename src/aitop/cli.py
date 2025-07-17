#!/usr/bin/env python3
"""
AITop 命令行界面模块
实现类似top的实时进程监控界面
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import psutil
import argparse


class AITopCLI:
    """AITop命令行界面类"""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.running = True
        self.start_time = datetime.now()
        self.collection_start_time = datetime.now()
        self.collected_data = []
        self.system_logs = []
        
        # 配置参数
        self.refresh_interval = args.refresh
        self.top_processes = args.top
        self.collection_duration = args.duration
        self.auto_report = args.auto_report
        self.output_path = args.output
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        self.running = False
        print("\n\n正在退出...")
        sys.exit(0)
    
    def _clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        try:
            # CPU信息
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            # 内存信息
            memory = psutil.virtual_memory()
            
            # 系统启动时间
            boot_time = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(boot_time)
            
            return {
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'load_avg': load_avg[0],
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'uptime': uptime,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"获取系统信息时出错: {e}")
            return {}
    
    def _get_top_processes(self) -> List[Dict[str, Any]]:
        """获取CPU和内存占用最高的进程"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'username']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] is not None:
                        # 获取内存使用量（MB）
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024) if pinfo['memory_info'] else 0
                        
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'][:20],  # 限制进程名长度
                            'cpu_percent': pinfo['cpu_percent'] or 0,
                            'memory_percent': pinfo['memory_percent'] or 0,
                            'memory_mb': memory_mb,
                            'status': pinfo['status'],
                            'username': pinfo['username'] or 'unknown'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"获取进程信息时出错: {e}")
            return []
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:self.top_processes]
    
    def _format_memory(self, bytes_value: int) -> str:
        """格式化内存显示"""
        if bytes_value >= 1024**3:  # GB
            return f"{bytes_value / (1024**3):.1f}GB"
        elif bytes_value >= 1024**2:  # MB
            return f"{bytes_value / (1024**2):.1f}MB"
        elif bytes_value >= 1024:  # KB
            return f"{bytes_value / 1024:.1f}KB"
        else:
            return f"{bytes_value}B"
    
    def _format_uptime(self, uptime: timedelta) -> str:
        """格式化运行时间"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}天{hours}小时"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def _get_collection_progress(self) -> tuple:
        """获取数据收集进度"""
        elapsed = (datetime.now() - self.collection_start_time).total_seconds()
        progress = min(elapsed / self.collection_duration, 1.0)
        return elapsed, progress
    
    def _display_header(self, system_info: Dict[str, Any]):
        """显示头部信息"""
        current_time = datetime.now().strftime("%H:%M:%S")
        uptime_str = self._format_uptime(system_info.get('uptime', timedelta(0)))
        
        print("\033[1m" + "="*80 + "\033[0m")
        print(f"\033[1mAITop - 智能系统监控 v1.0.0\033[0m" + " "*20 + f"更新时间: {current_time}")
        print("\033[1m" + "="*80 + "\033[0m")
        
        # 系统概览
        cpu_percent = system_info.get('cpu_percent', 0)
        memory_percent = system_info.get('memory_percent', 0)
        load_avg = system_info.get('load_avg', 0)
        
        print(f"系统概览: CPU: {cpu_percent:.1f}% | 内存: {memory_percent:.1f}% | "
              f"负载: {load_avg:.2f} | 运行时间: {uptime_str}")
        print()
    
    def _display_processes(self, processes: List[Dict[str, Any]]):
        """显示进程列表"""
        print(f"{'PID':<8} {'进程名称':<20} {'CPU%':<8} {'内存%':<8} {'内存使用':<10} {'状态':<8} {'用户':<12}")
        print("-" * 80)
        
        for proc in processes:
            memory_str = self._format_memory(proc['memory_mb'] * 1024 * 1024)
            status_map = {
                'running': '运行',
                'sleeping': '休眠',
                'disk-sleep': '磁盘休眠',
                'stopped': '停止',
                'zombie': '僵尸'
            }
            status = status_map.get(proc['status'], proc['status'])
            
            print(f"{proc['pid']:<8} {proc['name']:<20} {proc['cpu_percent']:<8.1f} "
                  f"{proc['memory_percent']:<8.1f} {memory_str:<10} {status:<8} {proc['username']:<12}")
    
    def _display_footer(self):
        """显示底部信息"""
        elapsed, progress = self._get_collection_progress()
        progress_bar = "█" * int(progress * 30) + "░" * (30 - int(progress * 30))
        
        print("\033[1m" + "="*80 + "\033[0m")
        print(f"数据收集中... (已收集 {elapsed:.0f}秒/{self.collection_duration}秒) "
              f"[{progress_bar}] {progress*100:.1f}%")
        print("按 'q' 退出 | 按 'r' 生成报告")
    
    def _collect_data_point(self, system_info: Dict[str, Any], processes: List[Dict[str, Any]]):
        """收集数据点"""
        data_point = {
            'timestamp': datetime.now(),
            'system': system_info,
            'processes': processes
        }
        self.collected_data.append(data_point)
    
    def _generate_report(self):
        """生成HTML报告"""
        if not self.collected_data:
            print("\n暂无数据可生成报告")
            return
        
        try:
            # 简化的分析
            analysis_result = self._simple_analysis()
            
            # 生成简单的HTML报告
            html_content = self._generate_simple_html(analysis_result)
            
            # 确保输出目录存在
            output_dir = os.path.dirname(self.output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 写入文件
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n报告已生成: {self.output_path}")
            
            # 自动打开浏览器
            if self.auto_report:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(self.output_path)}")
                
        except Exception as e:
            print(f"\n生成报告时出错: {e}")
    
    def _simple_analysis(self) -> Dict[str, Any]:
        """简化的数据分析"""
        if not self.collected_data:
            return {}
        
        # 计算基本统计
        cpu_values = []
        memory_values = []
        
        for item in self.collected_data:
            if 'system' in item and item['system']:
                cpu_values.append(item['system'].get('cpu_percent', 0))
                memory_values.append(item['system'].get('memory_percent', 0))
        
        if not cpu_values:
            return {}
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        
        # 计算健康评分
        health_score = 100
        if avg_cpu > 80:
            health_score -= 20
        if avg_memory > 80:
            health_score -= 20
        
        health_status = "良好" if health_score >= 80 else "一般" if health_score >= 60 else "需要关注"
        
        return {
            'avg_cpu': avg_cpu,
            'max_cpu': max_cpu,
            'avg_memory': avg_memory,
            'max_memory': max_memory,
            'health_score': health_score,
            'health_status': health_status,
            'data_points': len(self.collected_data)
        }
    
    def _generate_simple_html(self, analysis: Dict[str, Any]) -> str:
        """生成简化的HTML报告"""
        # 准备图表数据
        timestamps = []
        cpu_data = []
        memory_data = []
        
        for item in self.collected_data:
            if 'timestamp' in item and 'system' in item and item['system']:
                timestamps.append(item['timestamp'].strftime('%H:%M:%S'))
                cpu_data.append(item['system'].get('cpu_percent', 0))
                memory_data.append(item['system'].get('memory_percent', 0))
        
        # 最新进程数据
        latest_processes = self.collected_data[-1]['processes'] if self.collected_data else []
        
        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AITop 系统分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .metric {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 6px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .health-score {{ text-align: center; font-size: 3em; font-weight: bold; color: {health_color}; }}
        .process-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .process-table th, .process-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .process-table th {{ background: #f8f9fa; }}
        .chart-container {{ width: 100%; height: 400px; margin: 20px 0; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AITop 系统分析报告</h1>
            <p>生成时间: {generation_time} | 数据点: {data_points}</p>
        </div>
        
        <div class="card">
            <h2>系统健康状况</h2>
            <div class="health-score">{health_score}</div>
            <p style="text-align: center; font-size: 1.2em; color: #666;">{health_status}</p>
        </div>
        
        <div class="card">
            <h2>性能指标</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{avg_cpu:.1f}%</div>
                    <div class="metric-label">平均CPU</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{max_cpu:.1f}%</div>
                    <div class="metric-label">峰值CPU</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{avg_memory:.1f}%</div>
                    <div class="metric-label">平均内存</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{max_memory:.1f}%</div>
                    <div class="metric-label">峰值内存</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>性能趋势</h2>
            <canvas id="performanceChart" class="chart-container"></canvas>
        </div>
        
        <div class="card">
            <h2>进程分析</h2>
            <table class="process-table">
                <thead>
                    <tr>
                        <th>PID</th>
                        <th>进程名称</th>
                        <th>CPU%</th>
                        <th>内存%</th>
                        <th>内存使用</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    {process_rows}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {timestamps},
                datasets: [{{
                    label: 'CPU使用率',
                    data: {cpu_data},
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }}, {{
                    label: '内存使用率',
                    data: {memory_data},
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        # 生成进程表格行
        process_rows = ""
        for proc in latest_processes[:20]:
            memory_str = self._format_memory(proc['memory_mb'] * 1024 * 1024)
            status_map = {
                'running': '运行',
                'sleeping': '休眠',
                'disk-sleep': '磁盘休眠',
                'stopped': '停止',
                'zombie': '僵尸'
            }
            status = status_map.get(proc['status'], proc['status'])
            
            process_rows += f'''
                <tr>
                    <td>{proc['pid']}</td>
                    <td>{proc['name']}</td>
                    <td>{proc['cpu_percent']:.1f}%</td>
                    <td>{proc['memory_percent']:.1f}%</td>
                    <td>{memory_str}</td>
                    <td>{status}</td>
                </tr>
            '''
        
        # 健康状态颜色
        health_color = "#28a745" if analysis['health_score'] >= 80 else "#ffc107" if analysis['health_score'] >= 60 else "#dc3545"
        
        return html_template.format(
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data_points=analysis['data_points'],
            health_score=analysis['health_score'],
            health_status=analysis['health_status'],
            health_color=health_color,
            avg_cpu=analysis['avg_cpu'],
            max_cpu=analysis['max_cpu'],
            avg_memory=analysis['avg_memory'],
            max_memory=analysis['max_memory'],
            timestamps=timestamps,
            cpu_data=cpu_data,
            memory_data=memory_data,
            process_rows=process_rows
        )
    
    def run(self):
        """运行主循环"""
        print("正在启动AITop...")
        print("按 Ctrl+C 退出程序")
        time.sleep(1)
        
        try:
            while self.running:
                # 清屏
                self._clear_screen()
                
                # 获取系统信息
                system_info = self._get_system_info()
                if not system_info:
                    continue
                
                # 获取进程信息
                processes = self._get_top_processes()
                
                # 显示界面
                self._display_header(system_info)
                self._display_processes(processes)
                self._display_footer()
                
                # 收集数据
                self._collect_data_point(system_info, processes)
                
                # 检查是否需要生成报告
                elapsed, progress = self._get_collection_progress()
                if progress >= 1.0 and self.auto_report:
                    self._generate_report()
                    if not self.args.continuous:
                        break
                    else:
                        # 重新开始收集
                        self.collection_start_time = datetime.now()
                        self.collected_data = []
                
                # 等待刷新间隔
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
        except Exception as e:
            print(f"\n运行时出错: {e}")
        finally:
            # 如果有数据且用户要求，生成最终报告
            if self.collected_data and self.auto_report:
                print("\n正在生成最终报告...")
                self._generate_report()


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="AITop - 智能系统监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  aitop                          # 基本使用
  aitop --duration 300           # 收集5分钟数据
  aitop --refresh 2              # 每2秒刷新一次
  aitop --top 50                 # 显示前50个进程
  aitop --output report.html     # 指定报告输出路径
        """
    )
    
    parser.add_argument(
        '--refresh', '-r',
        type=int,
        default=1,
        help='界面刷新间隔（秒），默认1秒'
    )
    
    parser.add_argument(
        '--top', '-t',
        type=int,
        default=20,
        help='显示的进程数量，默认20个'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=120,
        help='数据收集时长（秒），默认120秒'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./reports/aitop_report.html',
        help='报告输出路径，默认./reports/aitop_report.html'
    )
    
    parser.add_argument(
        '--auto-report',
        action='store_true',
        default=True,
        help='收集完成后自动生成报告'
    )
    
    parser.add_argument(
        '--no-auto-report',
        action='store_false',
        dest='auto_report',
        help='不自动生成报告'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='连续模式，生成报告后继续监控'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='仅生成报告，不显示实时界面'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.report_only:
            # 仅报告模式
            print("正在收集数据...")
            cli = AITopCLI(args)
            
            # 收集指定时间的数据
            for i in range(args.duration):
                system_info = cli._get_system_info()
                processes = cli._get_top_processes()
                cli._collect_data_point(system_info, processes)
                
                print(f"\r进度: {i+1}/{args.duration} 秒", end='', flush=True)
                time.sleep(1)
            
            print("\n正在生成报告...")
            cli._generate_report()
        else:
            # 交互模式
            cli = AITopCLI(args)
            cli.run()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 