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
            # 使用完整的HTMLReportGenerator
            from reporter.html_generator import HTMLReportGenerator

            # 简化的分析
            analysis_result = self._simple_analysis()

            # 使用商业级报告生成器
            generator = HTMLReportGenerator()
            generator.generate_report(self.collected_data, analysis_result, self.output_path)

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
            return {
                'overall_health': 100,
                'key_findings': ['暂无数据'],
                'recommendations': [],
                'anomalies': [],
                'top_processes': []
            }

        # 计算基本统计
        cpu_values = []
        memory_values = []

        for item in self.collected_data:
            if 'system' in item and item['system']:
                cpu_values.append(item['system'].get('cpu_percent', 0))
                memory_values.append(item['system'].get('memory_percent', 0))

        if not cpu_values:
            return {
                'overall_health': 100,
                'key_findings': ['暂无有效数据'],
                'recommendations': [],
                'anomalies': [],
                'top_processes': []
            }

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

        # 生成关键发现
        key_findings = []
        if avg_cpu > 80:
            key_findings.append(f"CPU使用率较高，平均{avg_cpu:.1f}%")
        if avg_memory > 80:
            key_findings.append(f"内存使用率较高，平均{avg_memory:.1f}%")
        if not key_findings:
            key_findings.append("系统运行正常，所有指标在正常范围内")

        # 生成建议
        recommendations = []
        if avg_cpu > 80:
            recommendations.append({
                'title': 'CPU使用率优化',
                'description': '建议检查高CPU使用率的进程，考虑优化或升级硬件'
            })
        if avg_memory > 80:
            recommendations.append({
                'title': '内存使用率优化',
                'description': '建议检查内存使用情况，考虑增加内存或优化内存使用'
            })

        # 获取最新的进程数据
        top_processes = self.collected_data[-1]['processes'][:10] if self.collected_data else []

        return {
            'overall_health': health_score,
            'key_findings': key_findings,
            'recommendations': recommendations,
            'anomalies': [],
            'top_processes': top_processes
        }

    def _generate_simple_html(self, analysis: Dict[str, Any]) -> str:
        """生成简化的HTML报告 - 使用商业级大屏展示风格"""
        # 准备图表数据（优化性能）
        timestamps = []
        cpu_data = []
        memory_data = []

        # 数据采样以提高性能
        max_points = 100
        step = max(1, len(self.collected_data) // max_points)
        sampled_data = self.collected_data[::step]

        for item in sampled_data:
            if 'timestamp' in item and 'system' in item and item['system']:
                timestamps.append(item['timestamp'].strftime('%H:%M:%S'))
                cpu_data.append(item['system'].get('cpu_percent', 0))
                memory_data.append(item['system'].get('memory_percent', 0))

        # 最新进程数据（只显示前15个）
        latest_processes = self.collected_data[-1]['processes'][:15] if self.collected_data else []

        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AITop 智能监控大屏</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500;700&display=swap');

        :root {{
            --primary-color: #00ff88;
            --secondary-color: #0099ff;
            --accent-color: #ff6b35;
            --warning-color: #ffaa00;
            --error-color: #ff4444;
            --success-color: #00ff88;
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #2a2a2a;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --text-muted: #888888;
            --border-color: #333333;
            --glow-primary: 0 0 20px rgba(0, 255, 136, 0.3);
            --glow-secondary: 0 0 20px rgba(0, 153, 255, 0.3);
            --glow-warning: 0 0 20px rgba(255, 170, 0, 0.3);
            --glow-error: 0 0 20px rgba(255, 68, 68, 0.3);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Roboto', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
            background-image:
                radial-gradient(circle at 20% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 153, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(255, 107, 53, 0.1) 0%, transparent 50%);
            background-attachment: fixed;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1920px;
            margin: 0 auto;
            padding: 40px;
        }}

        .header {{
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 2px solid var(--primary-color);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: var(--glow-primary);
        }}

        .header-content {{
            max-width: 1920px;
            margin: 0 auto;
            padding: 0 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .header h1 {{
            font-family: 'Orbitron', monospace;
            font-size: 36px;
            font-weight: 900;
            color: var(--primary-color);
            text-shadow: var(--glow-primary);
            letter-spacing: 2px;
        }}

        .header-meta {{
            display: flex;
            gap: 30px;
            font-size: 14px;
            color: var(--text-secondary);
        }}

        .header-meta span {{
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            border: 1px solid var(--border-color);
        }}

        .card {{
            background: var(--surface-color);
            border-radius: var(--border-radius);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-light);
            border: 1px solid var(--border-color);
            transition: var(--transition);
        }}

        .card:hover {{
            box-shadow: var(--shadow-medium);
            transform: translateY(-2px);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-title {{
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }}

        .card-subtitle {{
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
        }}

        .grid {{
            display: grid;
            gap: 24px;
            margin-bottom: 32px;
        }}

        .grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}

        .health-card {{
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .health-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--success-color), var(--primary-color));
        }}

        .health-score {{
            font-size: 48px;
            font-weight: 700;
            color: {health_color};
            margin: 16px 0;
            letter-spacing: -1px;
        }}

        .health-status {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }}

        .metric-item {{
            background: var(--background-color);
            border-radius: var(--border-radius-small);
            padding: 20px;
            text-align: center;
            transition: var(--transition);
        }}

        .metric-item:hover {{
            background: #E5E5EA;
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}

        .metric-label {{
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .chart-container {{
            position: relative;
            height: 320px;
            margin: 20px 0;
            background: var(--background-color);
            border-radius: var(--border-radius-small);
            padding: 16px;
        }}

        .process-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: var(--surface-color);
            border-radius: var(--border-radius-small);
            overflow: hidden;
        }}

        .process-table th {{
            background: var(--background-color);
            padding: 16px 12px;
            text-align: left;
            font-weight: 600;
            color: var(--text-primary);
            font-size: 14px;
            letter-spacing: 0.3px;
        }}

        .process-table td {{
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
            color: var(--text-primary);
        }}

        .process-table tr:hover {{
            background: var(--background-color);
        }}

        .process-table tr:last-child td {{
            border-bottom: none;
        }}

        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 16px;
            }}

            .navbar-content {{
                padding: 0 16px;
                flex-direction: column;
                gap: 8px;
            }}

            .card {{
                padding: 16px;
            }}

            .metrics-grid {{
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }}

            .health-score {{
                font-size: 36px;
            }}

            .metric-value {{
                font-size: 24px;
            }}
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --background-color: #000000;
                --surface-color: #1C1C1E;
                --text-primary: #FFFFFF;
                --text-secondary: #8E8E93;
                --border-color: #38383A;
            }}

            .navbar {{
                background: rgba(28, 28, 30, 0.8);
            }}

            .metric-item:hover {{
                background: #2C2C2E;
            }}

            .process-table th {{
                background: #2C2C2E;
            }}

            .process-table tr:hover {{
                background: #2C2C2E;
            }}
        }}
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-content">
            <h1>AITop 系统分析报告</h1>
            <div class="meta">
                <span>生成时间: {generation_time}</span> •
                <span>数据点: {data_points}</span>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="grid grid-2">
            <div class="card health-card">
                <div class="card-header">
                    <h2 class="card-title">系统健康状况</h2>
                    <span class="card-subtitle">实时评估</span>
                </div>
                <div class="health-score">{health_score}</div>
                <div class="health-status">{health_status}</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">性能指标</h2>
                    <span class="card-subtitle">系统资源使用</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value">{avg_cpu:.1f}%</div>
                        <div class="metric-label">平均CPU</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">{max_cpu:.1f}%</div>
                        <div class="metric-label">峰值CPU</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">{avg_memory:.1f}%</div>
                        <div class="metric-label">平均内存</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">{max_memory:.1f}%</div>
                        <div class="metric-label">峰值内存</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">性能趋势</h2>
                <span class="card-subtitle">CPU和内存使用率变化</span>
            </div>
            <div class="chart-container">
                <div class="loading" id="chartLoading">
                    <div class="spinner"></div>
                </div>
                <canvas id="performanceChart" style="display: none;"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">进程分析</h2>
                <span class="card-subtitle">资源占用排行</span>
            </div>
            <div style="overflow-x: auto;">
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
    </div>

    <script>
        // 简化的图表实现，避免外部依赖
        class SimpleChart {{
            constructor(canvas, config) {{
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.config = config;
                this.data = config.data;
                this.options = config.options || {{}};
                this.init();
            }}

            init() {{
                this.canvas.width = this.canvas.offsetWidth;
                this.canvas.height = this.canvas.offsetHeight;
                this.draw();
            }}

            draw() {{
                const {{ ctx, canvas, data }} = this;
                const padding = 40;
                const width = canvas.width - padding * 2;
                const height = canvas.height - padding * 2;

                // 清空画布
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // 绘制背景
                ctx.fillStyle = '#F2F2F7';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                if (!data.labels || data.labels.length === 0) return;

                const stepX = width / (data.labels.length - 1);
                const maxY = Math.max(...data.datasets[0].data, ...data.datasets[1].data, 100);

                // 绘制网格线
                ctx.strokeStyle = '#E5E5EA';
                ctx.lineWidth = 1;
                for (let i = 0; i <= 5; i++) {{
                    const y = padding + (height / 5) * i;
                    ctx.beginPath();
                    ctx.moveTo(padding, y);
                    ctx.lineTo(padding + width, y);
                    ctx.stroke();
                }}

                // 绘制数据线
                data.datasets.forEach((dataset, index) => {{
                    ctx.strokeStyle = dataset.borderColor;
                    ctx.lineWidth = 3;
                    ctx.beginPath();

                    dataset.data.forEach((value, i) => {{
                        const x = padding + i * stepX;
                        const y = padding + height - (value / maxY) * height;
                        if (i === 0) {{
                            ctx.moveTo(x, y);
                        }} else {{
                            ctx.lineTo(x, y);
                        }}
                    }});

                    ctx.stroke();

                    // 绘制数据点
                    ctx.fillStyle = dataset.borderColor;
                    dataset.data.forEach((value, i) => {{
                        const x = padding + i * stepX;
                        const y = padding + height - (value / maxY) * height;
                        ctx.beginPath();
                        ctx.arc(x, y, 3, 0, 2 * Math.PI);
                        ctx.fill();
                    }});
                }});

                // 绘制标签
                ctx.fillStyle = '#8E8E93';
                ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
                ctx.textAlign = 'center';

                // Y轴标签
                for (let i = 0; i <= 5; i++) {{
                    const value = (maxY / 5) * (5 - i);
                    const y = padding + (height / 5) * i;
                    ctx.fillText(value.toFixed(0) + '%', 20, y + 4);
                }}

                // 图例
                ctx.textAlign = 'left';
                ctx.fillStyle = '#FF6384';
                ctx.fillRect(padding, 10, 12, 12);
                ctx.fillStyle = '#36A2EB';
                ctx.fillRect(padding + 80, 10, 12, 12);

                ctx.fillStyle = '#000';
                ctx.fillText('CPU使用率', padding + 18, 21);
                ctx.fillText('内存使用率', padding + 98, 21);
            }}
        }}

        // 延迟加载图表以提高性能
        setTimeout(() => {{
            const canvas = document.getElementById('performanceChart');
            const loading = document.getElementById('chartLoading');

            if (canvas) {{
                new SimpleChart(canvas, {{
                    type: 'line',
                    data: {{
                        labels: {timestamps},
                        datasets: [{{
                            label: 'CPU使用率',
                            data: {cpu_data},
                            borderColor: '#FF6384',
                            backgroundColor: 'rgba(255, 99, 132, 0.1)'
                        }}, {{
                            label: '内存使用率',
                            data: {memory_data},
                            borderColor: '#36A2EB',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)'
                        }}]
                    }}
                }});

                loading.style.display = 'none';
                canvas.style.display = 'block';
            }}
        }}, 500);

        // 响应式图表
        window.addEventListener('resize', () => {{
            const canvas = document.getElementById('performanceChart');
            if (canvas && canvas.chart) {{
                canvas.chart.init();
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