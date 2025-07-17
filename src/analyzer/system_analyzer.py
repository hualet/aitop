#!/usr/bin/env python3
"""
系统分析器
负责分析收集的系统数据，提供智能洞察和建议
"""

import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json


class SystemAnalyzer:
    """系统分析器"""
    
    def __init__(self):
        self.cpu_threshold_high = 80.0
        self.cpu_threshold_critical = 95.0
        self.memory_threshold_high = 80.0
        self.memory_threshold_critical = 95.0
        self.disk_threshold_high = 80.0
        self.disk_threshold_critical = 95.0
        
    def analyze(self, collected_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析收集的数据"""
        if not collected_data:
            return {'error': '没有数据可分析'}
        
        # 基本统计信息
        analysis_result = {
            'timestamp': datetime.now(),
            'data_points': len(collected_data),
            'time_range': self._get_time_range(collected_data),
            'system_health': self._analyze_system_health(collected_data),
            'cpu_analysis': self._analyze_cpu_usage(collected_data),
            'memory_analysis': self._analyze_memory_usage(collected_data),
            'process_analysis': self._analyze_processes(collected_data),
            'trends': self._analyze_trends(collected_data),
            'anomalies': self._detect_anomalies(collected_data),
            'recommendations': self._generate_recommendations(collected_data),
            'summary': {}
        }
        
        # 生成总结
        analysis_result['summary'] = self._generate_summary(analysis_result)
        
        return analysis_result
    
    def _get_time_range(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取数据时间范围"""
        timestamps = [item['timestamp'] for item in data if 'timestamp' in item]
        if not timestamps:
            return {}
        
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time
        
        return {
            'start': start_time,
            'end': end_time,
            'duration_seconds': duration.total_seconds(),
            'duration_formatted': str(duration)
        }
    
    def _analyze_system_health(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析系统健康状况"""
        if not data:
            return {}
        
        # 计算平均值
        cpu_values = []
        memory_values = []
        
        for item in data:
            if 'system' in item and item['system']:
                cpu_values.append(item['system'].get('cpu_percent', 0))
                memory_values.append(item['system'].get('memory_percent', 0))
        
        if not cpu_values or not memory_values:
            return {}
        
        avg_cpu = statistics.mean(cpu_values)
        avg_memory = statistics.mean(memory_values)
        max_cpu = max(cpu_values)
        max_memory = max(memory_values)
        
        # 计算健康评分 (0-100)
        health_score = 100
        
        # CPU影响
        if avg_cpu > self.cpu_threshold_critical:
            health_score -= 30
        elif avg_cpu > self.cpu_threshold_high:
            health_score -= 15
        
        # 内存影响
        if avg_memory > self.memory_threshold_critical:
            health_score -= 30
        elif avg_memory > self.memory_threshold_high:
            health_score -= 15
        
        # 峰值影响
        if max_cpu > self.cpu_threshold_critical:
            health_score -= 10
        if max_memory > self.memory_threshold_critical:
            health_score -= 10
        
        health_score = max(0, health_score)
        
        # 健康状态
        if health_score >= 80:
            status = "良好"
            status_color = "green"
        elif health_score >= 60:
            status = "一般"
            status_color = "yellow"
        else:
            status = "需要关注"
            status_color = "red"
        
        return {
            'health_score': health_score,
            'status': status,
            'status_color': status_color,
            'avg_cpu': avg_cpu,
            'avg_memory': avg_memory,
            'max_cpu': max_cpu,
            'max_memory': max_memory
        }
    
    def _analyze_cpu_usage(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析CPU使用情况"""
        cpu_values = []
        load_values = []
        
        for item in data:
            if 'system' in item and item['system']:
                cpu_values.append(item['system'].get('cpu_percent', 0))
                load_values.append(item['system'].get('load_avg', 0))
        
        if not cpu_values:
            return {}
        
        analysis = {
            'average': statistics.mean(cpu_values),
            'maximum': max(cpu_values),
            'minimum': min(cpu_values),
            'median': statistics.median(cpu_values),
            'std_deviation': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
            'load_average': statistics.mean(load_values) if load_values else 0,
            'high_usage_periods': [],
            'spikes': []
        }
        
        # 检测高使用率时段
        high_usage_count = sum(1 for cpu in cpu_values if cpu > self.cpu_threshold_high)
        analysis['high_usage_percentage'] = (high_usage_count / len(cpu_values)) * 100
        
        # 检测CPU峰值
        for i, cpu in enumerate(cpu_values):
            if cpu > self.cpu_threshold_critical:
                analysis['spikes'].append({
                    'index': i,
                    'value': cpu,
                    'timestamp': data[i]['timestamp'] if i < len(data) else None
                })
        
        # 趋势分析
        if len(cpu_values) > 5:
            recent_avg = statistics.mean(cpu_values[-5:])
            earlier_avg = statistics.mean(cpu_values[:5])
            analysis['trend'] = 'increasing' if recent_avg > earlier_avg * 1.1 else \
                              'decreasing' if recent_avg < earlier_avg * 0.9 else 'stable'
        else:
            analysis['trend'] = 'stable'
        
        return analysis
    
    def _analyze_memory_usage(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析内存使用情况"""
        memory_values = []
        memory_used_values = []
        
        for item in data:
            if 'system' in item and item['system']:
                memory_values.append(item['system'].get('memory_percent', 0))
                memory_used_values.append(item['system'].get('memory_used', 0))
        
        if not memory_values:
            return {}
        
        analysis = {
            'average_percent': statistics.mean(memory_values),
            'maximum_percent': max(memory_values),
            'minimum_percent': min(memory_values),
            'median_percent': statistics.median(memory_values),
            'std_deviation': statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
            'high_usage_periods': [],
            'memory_leaks': []
        }
        
        # 检测高内存使用率
        high_usage_count = sum(1 for mem in memory_values if mem > self.memory_threshold_high)
        analysis['high_usage_percentage'] = (high_usage_count / len(memory_values)) * 100
        
        # 检测可能的内存泄漏
        if len(memory_values) > 10:
            # 检查内存使用是否持续增长
            windows = [memory_values[i:i+5] for i in range(0, len(memory_values)-4, 5)]
            increasing_windows = 0
            
            for window in windows:
                if len(window) >= 2:
                    trend = window[-1] - window[0]
                    if trend > 5:  # 内存增长超过5%
                        increasing_windows += 1
            
            if increasing_windows > len(windows) * 0.6:  # 60%的窗口都在增长
                analysis['memory_leaks'].append({
                    'severity': 'warning',
                    'description': '检测到可能的内存泄漏模式',
                    'trend': 'increasing'
                })
        
        return analysis
    
    def _analyze_processes(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析进程情况"""
        all_processes = {}
        process_stats = {}
        
        for item in data:
            if 'processes' in item and item['processes']:
                for proc in item['processes']:
                    pid = proc['pid']
                    name = proc['name']
                    
                    if name not in all_processes:
                        all_processes[name] = {
                            'instances': [],
                            'cpu_usage': [],
                            'memory_usage': [],
                            'first_seen': item['timestamp'],
                            'last_seen': item['timestamp']
                        }
                    
                    all_processes[name]['instances'].append(proc)
                    all_processes[name]['cpu_usage'].append(proc.get('cpu_percent', 0))
                    all_processes[name]['memory_usage'].append(proc.get('memory_percent', 0))
                    all_processes[name]['last_seen'] = item['timestamp']
        
        # 分析每个进程
        for name, info in all_processes.items():
            if info['cpu_usage']:
                process_stats[name] = {
                    'avg_cpu': statistics.mean(info['cpu_usage']),
                    'max_cpu': max(info['cpu_usage']),
                    'avg_memory': statistics.mean(info['memory_usage']),
                    'max_memory': max(info['memory_usage']),
                    'instance_count': len(info['instances']),
                    'duration': (info['last_seen'] - info['first_seen']).total_seconds()
                }
        
        # 找出资源消耗最高的进程
        top_cpu_processes = sorted(
            process_stats.items(),
            key=lambda x: x[1]['avg_cpu'],
            reverse=True
        )[:10]
        
        top_memory_processes = sorted(
            process_stats.items(),
            key=lambda x: x[1]['avg_memory'],
            reverse=True
        )[:10]
        
        return {
            'total_unique_processes': len(all_processes),
            'top_cpu_processes': top_cpu_processes,
            'top_memory_processes': top_memory_processes,
            'process_stats': process_stats
        }
    
    def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析趋势"""
        if len(data) < 5:
            return {'error': '数据点不足，无法分析趋势'}
        
        # 提取时间序列数据
        timestamps = []
        cpu_values = []
        memory_values = []
        
        for item in data:
            if 'timestamp' in item and 'system' in item and item['system']:
                timestamps.append(item['timestamp'])
                cpu_values.append(item['system'].get('cpu_percent', 0))
                memory_values.append(item['system'].get('memory_percent', 0))
        
        trends = {}
        
        # CPU趋势
        if len(cpu_values) >= 5:
            trends['cpu'] = self._calculate_trend(cpu_values)
        
        # 内存趋势
        if len(memory_values) >= 5:
            trends['memory'] = self._calculate_trend(memory_values)
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """计算趋势"""
        if len(values) < 5:
            return {'trend': 'unknown'}
        
        # 简单线性回归
        n = len(values)
        x = list(range(n))
        
        # 计算斜率
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 判断趋势
        if abs(slope) < 0.1:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'slope': slope,
            'start_value': values[0],
            'end_value': values[-1],
            'change': values[-1] - values[0]
        }
    
    def _detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测异常"""
        anomalies = []
        
        # CPU异常
        cpu_values = []
        for item in data:
            if 'system' in item and item['system']:
                cpu_values.append((item['timestamp'], item['system'].get('cpu_percent', 0)))
        
        if len(cpu_values) > 5:
            cpu_anomalies = self._detect_value_anomalies(cpu_values, 'CPU', self.cpu_threshold_critical)
            anomalies.extend(cpu_anomalies)
        
        # 内存异常
        memory_values = []
        for item in data:
            if 'system' in item and item['system']:
                memory_values.append((item['timestamp'], item['system'].get('memory_percent', 0)))
        
        if len(memory_values) > 5:
            memory_anomalies = self._detect_value_anomalies(memory_values, '内存', self.memory_threshold_critical)
            anomalies.extend(memory_anomalies)
        
        return anomalies
    
    def _detect_value_anomalies(self, values: List[Tuple], metric_name: str, threshold: float) -> List[Dict[str, Any]]:
        """检测数值异常"""
        anomalies = []
        
        if len(values) < 5:
            return anomalies
        
        # 计算统计信息
        numeric_values = [v[1] for v in values]
        mean_val = statistics.mean(numeric_values)
        std_val = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
        
        # 检测异常值
        for timestamp, value in values:
            # 阈值异常
            if value > threshold:
                anomalies.append({
                    'type': 'threshold_exceeded',
                    'metric': metric_name,
                    'timestamp': timestamp,
                    'value': value,
                    'threshold': threshold,
                    'severity': 'high'
                })
            
            # 统计异常 (超过2个标准差)
            if std_val > 0 and abs(value - mean_val) > 2 * std_val:
                anomalies.append({
                    'type': 'statistical_anomaly',
                    'metric': metric_name,
                    'timestamp': timestamp,
                    'value': value,
                    'mean': mean_val,
                    'std_dev': std_val,
                    'severity': 'medium'
                })
        
        return anomalies
    
    def _generate_recommendations(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成建议"""
        recommendations = []
        
        if not data:
            return recommendations
        
        # 分析最新数据
        latest_data = data[-1] if data else {}
        system_info = latest_data.get('system', {})
        
        cpu_percent = system_info.get('cpu_percent', 0)
        memory_percent = system_info.get('memory_percent', 0)
        
        # CPU建议
        if cpu_percent > self.cpu_threshold_critical:
            recommendations.append({
                'type': 'cpu_high',
                'priority': 'high',
                'title': 'CPU使用率过高',
                'description': f'当前CPU使用率为{cpu_percent:.1f}%，建议检查高CPU使用率的进程',
                'actions': [
                    '使用top或htop查看占用CPU最高的进程',
                    '考虑终止不必要的进程',
                    '检查是否有进程陷入死循环',
                    '考虑升级硬件或优化应用程序'
                ]
            })
        elif cpu_percent > self.cpu_threshold_high:
            recommendations.append({
                'type': 'cpu_medium',
                'priority': 'medium',
                'title': 'CPU使用率较高',
                'description': f'当前CPU使用率为{cpu_percent:.1f}%，建议关注系统负载',
                'actions': [
                    '监控CPU使用率趋势',
                    '检查是否有不必要的后台进程',
                    '考虑在低峰时段运行计算密集型任务'
                ]
            })
        
        # 内存建议
        if memory_percent > self.memory_threshold_critical:
            recommendations.append({
                'type': 'memory_high',
                'priority': 'high',
                'title': '内存使用率过高',
                'description': f'当前内存使用率为{memory_percent:.1f}%，可能影响系统性能',
                'actions': [
                    '检查内存使用率最高的进程',
                    '考虑终止不必要的进程',
                    '清理系统缓存',
                    '考虑增加内存或启用swap'
                ]
            })
        elif memory_percent > self.memory_threshold_high:
            recommendations.append({
                'type': 'memory_medium',
                'priority': 'medium',
                'title': '内存使用率较高',
                'description': f'当前内存使用率为{memory_percent:.1f}%，建议优化内存使用',
                'actions': [
                    '监控内存使用趋势',
                    '检查是否有内存泄漏',
                    '考虑重启长时间运行的应用程序'
                ]
            })
        
        # 进程建议
        if 'processes' in latest_data and latest_data['processes']:
            top_processes = latest_data['processes'][:5]
            high_cpu_processes = [p for p in top_processes if p.get('cpu_percent', 0) > 50]
            
            if high_cpu_processes:
                recommendations.append({
                    'type': 'process_optimization',
                    'priority': 'medium',
                    'title': '发现高CPU使用率进程',
                    'description': f'发现{len(high_cpu_processes)}个高CPU使用率进程',
                    'actions': [
                        f'检查进程: {", ".join([p["name"] for p in high_cpu_processes])}',
                        '考虑优化或重启这些进程',
                        '检查进程是否正常工作'
                    ]
                })
        
        return recommendations
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析总结"""
        summary = {
            'health_status': analysis.get('system_health', {}).get('status', 'unknown'),
            'health_score': analysis.get('system_health', {}).get('health_score', 0),
            'key_findings': [],
            'critical_issues': [],
            'recommendations_count': len(analysis.get('recommendations', [])),
            'anomalies_count': len(analysis.get('anomalies', []))
        }
        
        # 关键发现
        cpu_analysis = analysis.get('cpu_analysis', {})
        memory_analysis = analysis.get('memory_analysis', {})
        
        if cpu_analysis.get('average', 0) > self.cpu_threshold_high:
            summary['key_findings'].append(f"CPU平均使用率较高: {cpu_analysis.get('average', 0):.1f}%")
        
        if memory_analysis.get('average_percent', 0) > self.memory_threshold_high:
            summary['key_findings'].append(f"内存平均使用率较高: {memory_analysis.get('average_percent', 0):.1f}%")
        
        # 严重问题
        high_priority_recommendations = [
            r for r in analysis.get('recommendations', [])
            if r.get('priority') == 'high'
        ]
        
        for rec in high_priority_recommendations:
            summary['critical_issues'].append(rec['title'])
        
        return summary 