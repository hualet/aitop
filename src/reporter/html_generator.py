#!/usr/bin/env python3
"""
HTML报告生成器
负责生成现代化的HTML5系统分析报告
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class HTMLReportGenerator:
    """HTML报告生成器"""
    
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
        
        # 生成HTML
        html_template = self._get_html_template()
        
        # 替换模板变量
        template_vars = {
            'title': "AITop 系统分析报告",
            'generation_time': report_data['report_info']['generation_time'],
            'analysis_duration': report_data['report_info']['analysis_duration'],
            'data_points': report_data['report_info']['data_points'],
            'health_score': report_data['health_summary']['health_score'],
            'health_status': report_data['health_summary']['health_status'],
            'status_color': report_data['health_summary']['status_color'],
            'avg_cpu': report_data['performance_metrics']['avg_cpu'],
            'max_cpu': report_data['performance_metrics']['max_cpu'],
            'avg_memory': report_data['performance_metrics']['avg_memory'],
            'max_memory': report_data['performance_metrics']['max_memory'],
            'key_findings_html': self._format_key_findings(report_data['health_summary']['key_findings']),
            'process_table_html': self._format_process_table(report_data['process_data']['latest_processes']),
            'recommendations_html': self._format_recommendations(report_data['recommendations']),
            'anomalies_html': self._format_anomalies(report_data['anomalies']),
            'report_data': json.dumps(report_data, ensure_ascii=False, default=str, indent=2)
        }
        
        html_content = html_template.format(**template_vars)
        
        return html_content
    
    def _prepare_report_data(self, collected_data: List[Dict[str, Any]], 
                            analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """准备报告数据"""
        
        # 基本信息
        time_range = analysis_result.get('time_range', {})
        system_health = analysis_result.get('system_health', {})
        summary = analysis_result.get('summary', {})
        
        # 图表数据
        chart_data = self._prepare_chart_data(collected_data)
        
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
                'status_color': system_health.get('status_color', 'gray'),
                'key_findings': summary.get('key_findings', []),
                'critical_issues': summary.get('critical_issues', [])
            },
            'performance_metrics': {
                'avg_cpu': system_health.get('avg_cpu', 0),
                'max_cpu': system_health.get('max_cpu', 0),
                'avg_memory': system_health.get('avg_memory', 0),
                'max_memory': system_health.get('max_memory', 0)
            },
            'chart_data': chart_data,
            'process_data': process_data,
            'recommendations': recommendations,
            'anomalies': anomalies,
            'trends': analysis_result.get('trends', {}),
            'cpu_analysis': analysis_result.get('cpu_analysis', {}),
            'memory_analysis': analysis_result.get('memory_analysis', {})
        }
    
    def _prepare_chart_data(self, collected_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """准备图表数据"""
        
        timestamps = []
        cpu_values = []
        memory_values = []
        
        for item in collected_data:
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
                latest_processes = latest_data['processes'][:20]  # 前20个进程
        
        return {
            'latest_processes': latest_processes,
            'top_cpu_processes': process_analysis.get('top_cpu_processes', [])[:10],
            'top_memory_processes': process_analysis.get('top_memory_processes', [])[:10],
            'total_unique_processes': process_analysis.get('total_unique_processes', 0)
        }
    
    def _get_system_platform(self, collected_data: List[Dict[str, Any]]) -> str:
        """获取系统平台信息"""
        if collected_data and 'system' in collected_data[0]:
            return "Linux"  # 默认，可以从系统信息中获取
        return "未知"
    
    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .card h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .health-score {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .health-score .score {{
            font-size: 4em;
            font-weight: bold;
            color: {status_color};
        }}
        
        .health-score .status {{
            font-size: 1.2em;
            color: #7f8c8d;
            margin-top: 10px;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .metric-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .metric-item .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        
        .metric-item .label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        
        .chart-container {{
            width: 100%;
            height: 300px;
            margin: 20px 0;
        }}
        
        .full-width {{
            grid-column: 1 / -1;
        }}
        
        .process-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .process-table th,
        .process-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .process-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .process-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .recommendations {{
            margin-top: 20px;
        }}
        
        .recommendation {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .recommendation.high {{
            background: #f8d7da;
            border-color: #f5c6cb;
        }}
        
        .recommendation h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        
        .recommendation.high h3 {{
            color: #721c24;
        }}
        
        .recommendation ul {{
            margin-left: 20px;
        }}
        
        .recommendation li {{
            margin-bottom: 5px;
        }}
        
        .key-findings {{
            list-style: none;
            padding: 0;
        }}
        
        .key-findings li {{
            background: #e3f2fd;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }}
        
        .anomaly {{
            background: #ffebee;
            border: 1px solid #ffcdd2;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .anomaly h4 {{
            color: #c62828;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AITop 系统分析报告</h1>
            <div class="meta">
                <span>生成时间: {generation_time}</span> | 
                <span>分析时长: {analysis_duration}</span> | 
                <span>数据点: {data_points}</span>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>系统健康状况</h2>
                <div class="health-score">
                    <div class="score">{health_score}</div>
                    <div class="status">{health_status}</div>
                </div>
                <div class="key-findings">
                    <h3>关键发现</h3>
                    <ul class="key-findings">
                        {key_findings_html}
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <h2>性能指标</h2>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="value">{avg_cpu:.1f}%</div>
                        <div class="label">平均CPU</div>
                    </div>
                    <div class="metric-item">
                        <div class="value">{max_cpu:.1f}%</div>
                        <div class="label">峰值CPU</div>
                    </div>
                    <div class="metric-item">
                        <div class="value">{avg_memory:.1f}%</div>
                        <div class="label">平均内存</div>
                    </div>
                    <div class="metric-item">
                        <div class="value">{max_memory:.1f}%</div>
                        <div class="label">峰值内存</div>
                    </div>
                </div>
            </div>
            
            <div class="card full-width">
                <h2>性能趋势</h2>
                <canvas id="performanceChart" class="chart-container"></canvas>
            </div>
            
            <div class="card full-width">
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
                        {process_table_html}
                    </tbody>
                </table>
            </div>
            
            <div class="card full-width">
                <h2>AI建议</h2>
                <div class="recommendations">
                    {recommendations_html}
                </div>
            </div>
            
            <div class="card full-width">
                <h2>异常检测</h2>
                <div class="anomalies">
                    {anomalies_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 图表数据
        const chartData = {report_data};
        
        // 性能趋势图
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.chart_data.timeline.labels,
                datasets: [{{
                    label: 'CPU使用率',
                    data: chartData.chart_data.timeline.cpu_data,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }}, {{
                    label: '内存使用率',
                    data: chartData.chart_data.timeline.memory_data,
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
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: 'CPU和内存使用率趋势'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    def _format_key_findings(self, key_findings: List[str]) -> str:
        """格式化关键发现"""
        if not key_findings:
            return '<li>系统运行正常，未发现异常</li>'
        
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
            return '<div class="recommendation"><h3>暂无建议</h3><p>系统运行正常，暂无需要关注的问题。</p></div>'
        
        html = ''
        for rec in recommendations:
            priority_class = 'high' if rec.get('priority') == 'high' else ''
            actions_html = ''.join([f'<li>{action}</li>' for action in rec.get('actions', [])])
            
            html += f'''
            <div class="recommendation {priority_class}">
                <h3>{rec.get('title', '')}</h3>
                <p>{rec.get('description', '')}</p>
                <ul>{actions_html}</ul>
            </div>
            '''
        return html
    
    def _format_anomalies(self, anomalies: List[Dict[str, Any]]) -> str:
        """格式化异常"""
        if not anomalies:
            return '<div class="anomaly"><h4>未检测到异常</h4><p>系统运行正常，未发现异常模式。</p></div>'
        
        html = ''
        for anomaly in anomalies:
            timestamp = anomaly.get('timestamp', datetime.now()).strftime('%H:%M:%S')
            html += f'''
            <div class="anomaly">
                <h4>{anomaly.get('type', '未知异常')} - {anomaly.get('metric', '')}</h4>
                <p>时间: {timestamp}</p>
                <p>数值: {anomaly.get('value', 0):.1f}</p>
                <p>严重程度: {anomaly.get('severity', '未知')}</p>
            </div>
            '''
        return html 