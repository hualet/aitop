#!/usr/bin/env python3
"""
HTML报告生成器 - 商业级大屏展示风格
负责生成高端商业展示用的HTML5系统分析报告
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class HTMLReportGenerator:
    """HTML报告生成器 - 商业级大屏展示风格"""

    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        self.static_dir = Path(__file__).parent / 'static'

    def generate_report(self, collected_data: List[Dict[str, Any]],
                       analysis_result: Dict[str, Any],
                       output_path: str) -> str:
        """生成HTML报告"""

        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 生成HTML内容
        html_content = self._generate_html_content(collected_data, analysis_result)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file.absolute())

    def _generate_html_content(self, collected_data: List[Dict[str, Any]],
                              analysis_result: Dict[str, Any]) -> str:
        """生成HTML内容"""

        # 准备数据
        report_data = self._prepare_report_data(collected_data, analysis_result)

        # 生成优化的图表数据（分页处理）
        chart_data = self._prepare_optimized_chart_data(collected_data)

        # 生成HTML
        html_template = self._get_dashboard_template()

        # 替换模板变量
        template_vars = {
            'title': "AITop 智能监控大屏",
            'generation_time': report_data['report_info']['generation_time'],
            'analysis_duration': report_data['report_info']['analysis_duration'],
            'data_points': report_data['report_info']['data_points'],
            'health_score': report_data['health_summary']['health_score'],
            'health_status': report_data['health_summary']['health_status'],
            'status_color': self._get_status_color(report_data['health_summary']['health_score']),
            'avg_cpu': report_data['performance_metrics']['avg_cpu'],
            'max_cpu': report_data['performance_metrics']['max_cpu'],
            'avg_memory': report_data['performance_metrics']['avg_memory'],
            'max_memory': report_data['performance_metrics']['max_memory'],
            'key_findings_html': self._format_key_findings(report_data['health_summary']['key_findings']),
            'process_table_html': self._format_process_table(report_data['process_data']['latest_processes']),
            'recommendations_html': self._format_recommendations(report_data['recommendations']),
            'anomalies_html': self._format_anomalies(report_data['anomalies']),
            'chart_data_json': json.dumps(chart_data, ensure_ascii=False, separators=(',', ':'))
        }

        html_content = html_template.format(**template_vars)

        return html_content

    def _get_status_color(self, score: float) -> str:
        """根据健康评分获取状态颜色"""
        if score >= 80:
            return "#00ff88"  # 绿色
        elif score >= 60:
            return "#ffaa00"  # 橙色
        else:
            return "#ff4444"  # 红色

    def _prepare_report_data(self, collected_data: List[Dict[str, Any]],
                            analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """准备报告数据"""

        # 基本信息
        time_range = analysis_result.get('time_range', {})
        system_health = analysis_result.get('system_health', {})
        summary = analysis_result.get('summary', {})

        # 进程数据
        process_data = self._prepare_process_data(collected_data, analysis_result)

        # 建议数据
        recommendations = analysis_result.get('recommendations', [])

        # 异常数据
        anomalies = analysis_result.get('anomalies', [])

        return {
            'report_info': {
                'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_points': len(collected_data),
                'analysis_duration': time_range.get('duration_formatted', '未知'),
                'system_platform': self._get_system_platform(collected_data)
            },
            'health_summary': {
                'health_score': system_health.get('health_score', 0),
                'health_status': system_health.get('status', '未知'),
                'key_findings': summary.get('key_findings', []),
                'critical_issues': summary.get('critical_issues', [])
            },
            'performance_metrics': {
                'avg_cpu': system_health.get('avg_cpu', 0),
                'max_cpu': system_health.get('max_cpu', 0),
                'avg_memory': system_health.get('avg_memory', 0),
                'max_memory': system_health.get('max_memory', 0)
            },
            'process_data': process_data,
            'recommendations': recommendations,
            'anomalies': anomalies,
            'trends': analysis_result.get('trends', {}),
            'cpu_analysis': analysis_result.get('cpu_analysis', {}),
            'memory_analysis': analysis_result.get('memory_analysis', {})
        }

    def _prepare_optimized_chart_data(self, collected_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """准备优化的图表数据 - 只保留关键数据点"""

        # 如果数据点过多，进行采样
        max_points = 50
        step = max(1, len(collected_data) // max_points)

        sampled_data = collected_data[::step]

        timestamps = []
        cpu_values = []
        memory_values = []

        for item in sampled_data:
            if 'timestamp' in item and 'system' in item and item['system']:
                timestamps.append(item['timestamp'].strftime('%H:%M:%S'))
                cpu_values.append(item['system'].get('cpu_percent', 0))
                memory_values.append(item['system'].get('memory_percent', 0))

        return {
            'timeline': {
                'labels': timestamps,
                'cpu_data': cpu_values,
                'memory_data': memory_values
            },
            'cpu_distribution': self._calculate_distribution(cpu_values),
            'memory_distribution': self._calculate_distribution(memory_values)
        }

    def _calculate_distribution(self, values: List[float]) -> Dict[str, int]:
        """计算数值分布"""
        if not values:
            return {}

        distribution = {
            'low': 0,      # 0-30%
            'medium': 0,   # 30-70%
            'high': 0,     # 70-90%
            'critical': 0  # 90%+
        }

        for value in values:
            if value < 30:
                distribution['low'] += 1
            elif value < 70:
                distribution['medium'] += 1
            elif value < 90:
                distribution['high'] += 1
            else:
                distribution['critical'] += 1

        return distribution

    def _prepare_process_data(self, collected_data: List[Dict[str, Any]],
                             analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """准备进程数据"""

        process_analysis = analysis_result.get('process_analysis', {})

        # 获取最新的进程数据
        latest_processes = []
        if collected_data:
            latest_data = collected_data[-1]
            if 'processes' in latest_data:
                latest_processes = latest_data['processes'][:10]  # 只显示前10个进程

        return {
            'latest_processes': latest_processes,
            'top_cpu_processes': process_analysis.get('top_cpu_processes', [])[:10],
            'top_memory_processes': process_analysis.get('top_memory_processes', [])[:10],
            'total_unique_processes': process_analysis.get('total_unique_processes', 0)
        }

    def _get_system_platform(self, collected_data: List[Dict[str, Any]]) -> str:
        """获取系统平台信息"""
        if collected_data and 'system' in collected_data[0]:
            return "Enterprise Server"
        return "Unknown"

    def _get_dashboard_template(self) -> str:
        """获取商业级大屏展示模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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

        /* 顶部导航栏 */
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

        /* 主容器 */
        .dashboard {{
            max-width: 1920px;
            margin: 0 auto;
            padding: 40px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: auto auto auto;
            gap: 30px;
            min-height: calc(100vh - 120px);
        }}

        /* 卡片样式 */
        .card {{
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9), rgba(42, 42, 42, 0.9));
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            opacity: 0.8;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), var(--glow-primary);
        }}

        .card-title {{
            font-family: 'Orbitron', monospace;
            font-size: 18px;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* 健康状态卡片 */
        .health-card {{
            grid-column: 1;
            grid-row: 1;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(26, 26, 26, 0.9));
        }}

        .health-score {{
            font-family: 'Orbitron', monospace;
            font-size: 72px;
            font-weight: 900;
            color: {status_color};
            text-shadow: 0 0 30px {status_color};
            margin: 20px 0;
            animation: pulse 2s infinite;
        }}

        .health-status {{
            font-size: 24px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        /* 性能指标卡片 */
        .metrics-card {{
            grid-column: 2 / 4;
            grid-row: 1;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 20px;
        }}

        .metric-item {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .metric-item:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: scale(1.05);
        }}

        .metric-value {{
            font-family: 'Orbitron', monospace;
            font-size: 36px;
            font-weight: 700;
            color: var(--secondary-color);
            text-shadow: var(--glow-secondary);
            margin-bottom: 10px;
        }}

        .metric-label {{
            font-size: 14px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* 图表卡片 */
        .chart-card {{
            grid-column: 1 / 4;
            grid-row: 2;
            min-height: 400px;
        }}

        .chart-container {{
            position: relative;
            height: 350px;
            margin-top: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }}

        /* 进程表格卡片 */
        .process-card {{
            grid-column: 1 / 3;
            grid-row: 3;
        }}

        .process-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            overflow: hidden;
        }}

        .process-table th {{
            background: rgba(0, 255, 136, 0.2);
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            color: var(--primary-color);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid var(--primary-color);
        }}

        .process-table td {{
            padding: 12px 10px;
            border-bottom: 1px solid var(--border-color);
            font-size: 13px;
            color: var(--text-secondary);
        }}

        .process-table tr:hover {{
            background: rgba(0, 255, 136, 0.1);
        }}

        .process-table tr:last-child td {{
            border-bottom: none;
        }}

        /* 状态卡片 */
        .status-card {{
            grid-column: 3;
            grid-row: 3;
        }}

        .status-item {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid var(--accent-color);
        }}

        .status-item h4 {{
            color: var(--accent-color);
            font-size: 16px;
            margin-bottom: 10px;
        }}

        .status-item p {{
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.4;
        }}

        /* 关键发现 */
        .key-findings {{
            list-style: none;
            padding: 0;
        }}

        .key-findings li {{
            background: rgba(0, 255, 136, 0.1);
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            font-size: 14px;
            color: var(--text-secondary);
            transition: all 0.3s ease;
        }}

        .key-findings li:hover {{
            background: rgba(0, 255, 136, 0.2);
            transform: translateX(5px);
        }}

        /* 加载动画 */
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }}

        .spinner {{
            width: 60px;
            height: 60px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* 响应式设计 */
        @media (max-width: 1600px) {{
            .dashboard {{
                grid-template-columns: 1fr 1fr;
                padding: 20px;
            }}

            .health-card {{
                grid-column: 1;
                grid-row: 1;
            }}

            .metrics-card {{
                grid-column: 2;
                grid-row: 1;
            }}

            .chart-card {{
                grid-column: 1 / 3;
                grid-row: 2;
            }}

            .process-card {{
                grid-column: 1;
                grid-row: 3;
            }}

            .status-card {{
                grid-column: 2;
                grid-row: 3;
            }}
        }}

        @media (max-width: 1024px) {{
            .dashboard {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}

            .health-card,
            .metrics-card,
            .chart-card,
            .process-card,
            .status-card {{
                grid-column: 1;
                grid-row: auto;
            }}

            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .health-score {{
                font-size: 48px;
            }}

            .metric-value {{
                font-size: 24px;
            }}
        }}

        /* 滚动条样式 */
        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--primary-color);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--secondary-color);
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>AITop 智能监控大屏</h1>
            <div class="header-meta">
                <span>生成时间: {generation_time}</span>
                <span>分析时长: {analysis_duration}</span>
                <span>数据点: {data_points}</span>
            </div>
        </div>
    </div>

    <div class="dashboard">
        <div class="card health-card">
            <div class="card-title">系统健康状况</div>
            <div class="health-score">{health_score}</div>
            <div class="health-status">{health_status}</div>
            <div style="margin-top: 30px;">
                <ul class="key-findings">
                    {key_findings_html}
                </ul>
            </div>
        </div>

        <div class="card metrics-card">
            <div class="card-title">性能指标概览</div>
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

        <div class="card chart-card">
            <div class="card-title">实时性能趋势</div>
            <div class="chart-container">
                <div class="loading" id="chartLoading">
                    <div class="spinner"></div>
                </div>
                <canvas id="performanceChart" style="display: none;"></canvas>
            </div>
        </div>

        <div class="card process-card">
            <div class="card-title">进程资源占用</div>
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
                        {process_table_html}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card status-card">
            <div class="card-title">系统状态</div>
            <div class="status-content">
                {recommendations_html}
                {anomalies_html}
            </div>
        </div>
    </div>

    <script>
        // 高性能图表实现
        class DashboardChart {{
            constructor(canvas, config) {{
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.config = config;
                this.data = config.data;
                this.options = config.options || {{}};
                this.init();
            }}

            init() {{
                const displayWidth = this.canvas.offsetWidth;
                const displayHeight = this.canvas.offsetHeight;

                this.canvas.width = displayWidth * 2;
                this.canvas.height = displayHeight * 2;
                this.canvas.style.width = displayWidth + 'px';
                this.canvas.style.height = displayHeight + 'px';
                this.ctx.scale(2, 2);
                this.draw();
            }}

            draw() {{
                const {{ ctx, canvas, data }} = this;
                const width = canvas.width / 2;
                const height = canvas.height / 2;
                const padding = 60;
                const chartWidth = width - padding * 2;
                const chartHeight = height - padding * 2;

                // 清空画布
                ctx.clearRect(0, 0, width, height);

                // 绘制背景网格
                this.drawGrid(ctx, padding, chartWidth, chartHeight);

                if (!data.labels || data.labels.length === 0) return;

                const stepX = chartWidth / (data.labels.length - 1);
                const maxY = Math.max(...data.datasets[0].data, ...data.datasets[1].data, 100);

                // 绘制数据线
                data.datasets.forEach((dataset, index) => {{
                    this.drawLine(ctx, dataset, padding, chartWidth, chartHeight, stepX, maxY);
                }});

                // 绘制标签
                this.drawLabels(ctx, data.labels, padding, chartWidth, chartHeight, maxY);

                // 绘制图例
                this.drawLegend(ctx, data.datasets, padding);
            }}

            drawGrid(ctx, padding, width, height) {{
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                ctx.lineWidth = 1;

                // 水平网格线
                for (let i = 0; i <= 5; i++) {{
                    const y = padding + (height / 5) * i;
                    ctx.beginPath();
                    ctx.moveTo(padding, y);
                    ctx.lineTo(padding + width, y);
                    ctx.stroke();
                }}

                // 垂直网格线
                for (let i = 0; i <= 10; i++) {{
                    const x = padding + (width / 10) * i;
                    ctx.beginPath();
                    ctx.moveTo(x, padding);
                    ctx.lineTo(x, padding + height);
                    ctx.stroke();
                }}
            }}

            drawLine(ctx, dataset, padding, width, height, stepX, maxY) {{
                // 绘制发光效果
                ctx.shadowColor = dataset.borderColor;
                ctx.shadowBlur = 10;
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

                // 重置阴影
                ctx.shadowBlur = 0;

                // 绘制数据点
                ctx.fillStyle = dataset.borderColor;
                dataset.data.forEach((value, i) => {{
                    const x = padding + i * stepX;
                    const y = padding + height - (value / maxY) * height;
                    ctx.beginPath();
                    ctx.arc(x, y, 4, 0, 2 * Math.PI);
                    ctx.fill();
                }});
            }}

            drawLabels(ctx, labels, padding, width, height, maxY) {{
                ctx.fillStyle = '#cccccc';
                ctx.font = '12px Roboto';
                ctx.textAlign = 'center';

                // Y轴标签
                ctx.textAlign = 'right';
                for (let i = 0; i <= 5; i++) {{
                    const value = (maxY / 5) * (5 - i);
                    const y = padding + (height / 5) * i;
                    ctx.fillText(value.toFixed(0) + '%', padding - 10, y + 4);
                }}

                // X轴标签（只显示部分）
                ctx.textAlign = 'center';
                const step = Math.ceil(labels.length / 8);
                labels.forEach((label, i) => {{
                    if (i % step === 0) {{
                        const x = padding + (width / (labels.length - 1)) * i;
                        ctx.fillText(label, x, padding + height + 20);
                    }}
                }});
            }}

            drawLegend(ctx, datasets, padding) {{
                ctx.font = '14px Roboto';
                ctx.textAlign = 'left';

                datasets.forEach((dataset, index) => {{
                    const y = 30 + index * 25;

                    // 绘制颜色块
                    ctx.fillStyle = dataset.borderColor;
                    ctx.fillRect(padding, y - 8, 16, 16);

                    // 绘制文本
                    ctx.fillStyle = '#ffffff';
                    ctx.fillText(dataset.label, padding + 25, y + 4);
                }});
            }}
        }}

        // 图表数据
        const chartData = {chart_data_json};

        // 延迟加载图表
        setTimeout(() => {{
            const canvas = document.getElementById('performanceChart');
            const loading = document.getElementById('chartLoading');

            if (canvas && chartData.timeline) {{
                new DashboardChart(canvas, {{
                    type: 'line',
                    data: {{
                        labels: chartData.timeline.labels,
                        datasets: [{{
                            label: 'CPU使用率',
                            data: chartData.timeline.cpu_data,
                            borderColor: '#00ff88',
                            backgroundColor: 'rgba(0, 255, 136, 0.1)'
                        }}, {{
                            label: '内存使用率',
                            data: chartData.timeline.memory_data,
                            borderColor: '#0099ff',
                            backgroundColor: 'rgba(0, 153, 255, 0.1)'
                        }}]
                    }}
                }});

                loading.style.display = 'none';
                canvas.style.display = 'block';
            }}
        }}, 1000);

        // 实时更新效果
        setInterval(() => {{
            const healthScore = document.querySelector('.health-score');
            if (healthScore) {{
                healthScore.style.textShadow = `0 0 30px {status_color}, 0 0 60px {status_color}`;
            }}
        }}, 2000);

        // 响应式图表
        let resizeTimeout;
        window.addEventListener('resize', () => {{
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {{
                const canvas = document.getElementById('performanceChart');
                if (canvas && canvas.chart) {{
                    canvas.chart.init();
                }}
            }}, 300);
        }});
    </script>
</body>
</html>'''

    def _format_key_findings(self, key_findings: List[str]) -> str:
        """格式化关键发现"""
        if not key_findings:
            return '<li>系统运行正常，所有指标在正常范围内</li>'

        html = ''
        for finding in key_findings:
            html += f'<li>{finding}</li>'
        return html

    def _format_process_table(self, processes: List[Dict[str, Any]]) -> str:
        """格式化进程表格"""
        if not processes:
            return '<tr><td colspan="6">暂无进程数据</td></tr>'

        html = ''
        for proc in processes:
            memory_mb = proc.get('memory_mb', 0)
            memory_str = f"{memory_mb:.1f}MB" if memory_mb < 1024 else f"{memory_mb/1024:.1f}GB"

            status_map = {
                'running': '运行',
                'sleeping': '休眠',
                'disk-sleep': '磁盘休眠',
                'stopped': '停止',
                'zombie': '僵尸'
            }
            status = status_map.get(proc.get('status', ''), proc.get('status', ''))

            html += f'''
            <tr>
                <td>{proc.get('pid', '')}</td>
                <td>{proc.get('name', '')}</td>
                <td>{proc.get('cpu_percent', 0):.1f}%</td>
                <td>{proc.get('memory_percent', 0):.1f}%</td>
                <td>{memory_str}</td>
                <td>{status}</td>
            </tr>
            '''
        return html

    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """格式化建议"""
        if not recommendations:
            return '<div class="status-item"><h4>系统状态良好</h4><p>所有系统指标正常，无需特别关注。</p></div>'

        html = ''
        for rec in recommendations:
            html += f'''
            <div class="status-item">
                <h4>{rec.get('title', '系统建议')}</h4>
                <p>{rec.get('description', '')}</p>
            </div>
            '''
        return html

    def _format_anomalies(self, anomalies: List[Dict[str, Any]]) -> str:
        """格式化异常"""
        if not anomalies:
            return '<div class="status-item"><h4>无异常检测</h4><p>系统运行稳定，未发现异常模式。</p></div>'

        html = ''
        for anomaly in anomalies:
            timestamp = anomaly.get('timestamp', datetime.now()).strftime('%H:%M:%S')
            html += f'''
            <div class="status-item">
                <h4>{anomaly.get('type', '异常检测')} - {timestamp}</h4>
                <p>{anomaly.get('metric', '')}: {anomaly.get('value', 0):.1f} ({anomaly.get('severity', '未知')})</p>
            </div>
            '''
        return html