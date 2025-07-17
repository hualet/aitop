#!/usr/bin/env python3
"""
系统日志收集器
负责收集和分析系统日志
"""

import os
import re
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json


class LogCollector:
    """系统日志收集器"""
    
    def __init__(self):
        self.log_levels = ['emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug']
        self.important_services = [
            'systemd', 'kernel', 'sshd', 'cron', 'NetworkManager', 
            'docker', 'nginx', 'apache2', 'mysql', 'postgresql'
        ]
    
    def _run_command(self, cmd: List[str]) -> str:
        """运行系统命令"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return ""
    
    def collect_journalctl_logs(self, since_minutes: int = 30, max_lines: int = 1000) -> List[Dict[str, Any]]:
        """收集journalctl日志"""
        logs = []
        
        try:
            # 构建journalctl命令
            since_time = datetime.now() - timedelta(minutes=since_minutes)
            since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cmd = [
                'journalctl',
                '--since', since_str,
                '--output=json',
                '--no-pager',
                '--lines', str(max_lines)
            ]
            
            output = self._run_command(cmd)
            if not output:
                return logs
            
            # 解析JSON格式的日志
            for line in output.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    log_entry = json.loads(line)
                    
                    # 提取关键信息
                    timestamp = datetime.fromtimestamp(int(log_entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
                    
                    logs.append({
                        'timestamp': timestamp,
                        'level': self._get_log_level(log_entry),
                        'service': log_entry.get('_SYSTEMD_UNIT', log_entry.get('SYSLOG_IDENTIFIER', 'unknown')),
                        'message': log_entry.get('MESSAGE', ''),
                        'pid': log_entry.get('_PID'),
                        'uid': log_entry.get('_UID'),
                        'hostname': log_entry.get('_HOSTNAME'),
                        'facility': log_entry.get('SYSLOG_FACILITY'),
                        'raw': log_entry
                    })
                except (json.JSONDecodeError, ValueError):
                    continue
                    
        except Exception as e:
            print(f"收集journalctl日志时出错: {e}")
        
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
    
    def _get_log_level(self, log_entry: Dict[str, Any]) -> str:
        """从日志条目中提取日志级别"""
        priority = log_entry.get('PRIORITY', '6')
        try:
            level_index = int(priority)
            if 0 <= level_index < len(self.log_levels):
                return self.log_levels[level_index]
        except (ValueError, IndexError):
            pass
        return 'info'
    
    def collect_system_errors(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """收集系统错误日志"""
        errors = []
        
        try:
            since_time = datetime.now() - timedelta(minutes=since_minutes)
            since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cmd = [
                'journalctl',
                '--since', since_str,
                '--priority=err',
                '--output=json',
                '--no-pager',
                '--lines', '500'
            ]
            
            output = self._run_command(cmd)
            if not output:
                return errors
            
            for line in output.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    log_entry = json.loads(line)
                    timestamp = datetime.fromtimestamp(int(log_entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
                    
                    errors.append({
                        'timestamp': timestamp,
                        'level': self._get_log_level(log_entry),
                        'service': log_entry.get('_SYSTEMD_UNIT', log_entry.get('SYSLOG_IDENTIFIER', 'unknown')),
                        'message': log_entry.get('MESSAGE', ''),
                        'severity': 'error'
                    })
                except (json.JSONDecodeError, ValueError):
                    continue
                    
        except Exception as e:
            print(f"收集系统错误日志时出错: {e}")
        
        return sorted(errors, key=lambda x: x['timestamp'], reverse=True)
    
    def collect_service_logs(self, service_name: str, since_minutes: int = 30) -> List[Dict[str, Any]]:
        """收集特定服务的日志"""
        logs = []
        
        try:
            since_time = datetime.now() - timedelta(minutes=since_minutes)
            since_str = since_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cmd = [
                'journalctl',
                '--unit', service_name,
                '--since', since_str,
                '--output=json',
                '--no-pager',
                '--lines', '200'
            ]
            
            output = self._run_command(cmd)
            if not output:
                return logs
            
            for line in output.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    log_entry = json.loads(line)
                    timestamp = datetime.fromtimestamp(int(log_entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
                    
                    logs.append({
                        'timestamp': timestamp,
                        'level': self._get_log_level(log_entry),
                        'service': service_name,
                        'message': log_entry.get('MESSAGE', ''),
                        'pid': log_entry.get('_PID')
                    })
                except (json.JSONDecodeError, ValueError):
                    continue
                    
        except Exception as e:
            print(f"收集服务 {service_name} 日志时出错: {e}")
        
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
    
    def analyze_log_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析日志模式"""
        if not logs:
            return {}
        
        analysis = {
            'total_entries': len(logs),
            'time_range': {
                'start': min(log['timestamp'] for log in logs),
                'end': max(log['timestamp'] for log in logs)
            },
            'level_distribution': {},
            'service_distribution': {},
            'error_patterns': [],
            'frequent_messages': {},
            'timeline': []
        }
        
        # 统计日志级别分布
        for log in logs:
            level = log['level']
            analysis['level_distribution'][level] = analysis['level_distribution'].get(level, 0) + 1
        
        # 统计服务分布
        for log in logs:
            service = log['service']
            analysis['service_distribution'][service] = analysis['service_distribution'].get(service, 0) + 1
        
        # 分析错误模式
        error_logs = [log for log in logs if log['level'] in ['emerg', 'alert', 'crit', 'err']]
        analysis['error_patterns'] = self._extract_error_patterns(error_logs)
        
        # 统计频繁消息
        message_counts = {}
        for log in logs:
            message = log['message'][:100]  # 取前100个字符
            message_counts[message] = message_counts.get(message, 0) + 1
        
        # 取前10个最频繁的消息
        analysis['frequent_messages'] = dict(
            sorted(message_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # 创建时间线（按小时分组）
        timeline = {}
        for log in logs:
            hour_key = log['timestamp'].strftime('%Y-%m-%d %H:00')
            if hour_key not in timeline:
                timeline[hour_key] = {'total': 0, 'errors': 0}
            timeline[hour_key]['total'] += 1
            if log['level'] in ['emerg', 'alert', 'crit', 'err']:
                timeline[hour_key]['errors'] += 1
        
        analysis['timeline'] = [
            {'time': k, 'total': v['total'], 'errors': v['errors']}
            for k, v in sorted(timeline.items())
        ]
        
        return analysis
    
    def _extract_error_patterns(self, error_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取错误模式"""
        patterns = []
        
        # 常见错误模式
        common_patterns = [
            (r'failed to start', '服务启动失败'),
            (r'connection refused', '连接被拒绝'),
            (r'permission denied', '权限拒绝'),
            (r'no such file or directory', '文件或目录不存在'),
            (r'out of memory', '内存不足'),
            (r'disk full', '磁盘空间不足'),
            (r'timeout', '超时'),
            (r'segmentation fault', '段错误'),
            (r'core dumped', '核心转储')
        ]
        
        for pattern, description in common_patterns:
            matching_logs = [
                log for log in error_logs 
                if re.search(pattern, log['message'].lower())
            ]
            
            if matching_logs:
                patterns.append({
                    'pattern': pattern,
                    'description': description,
                    'count': len(matching_logs),
                    'recent_examples': matching_logs[:3]
                })
        
        return patterns
    
    def collect_all_logs(self, since_minutes: int = 30) -> Dict[str, Any]:
        """收集所有日志信息"""
        # 收集基本日志
        all_logs = self.collect_journalctl_logs(since_minutes)
        
        # 收集错误日志
        error_logs = self.collect_system_errors(since_minutes * 2)  # 错误日志收集更长时间
        
        # 收集重要服务日志
        service_logs = {}
        for service in self.important_services:
            service_logs[service] = self.collect_service_logs(service, since_minutes)
        
        # 分析日志模式
        analysis = self.analyze_log_patterns(all_logs)
        
        return {
            'timestamp': datetime.now(),
            'collection_period_minutes': since_minutes,
            'all_logs': all_logs,
            'error_logs': error_logs,
            'service_logs': service_logs,
            'analysis': analysis
        } 