#!/usr/bin/env python3
"""
系统数据收集器
负责收集CPU、内存、磁盘、网络等系统资源使用情况
"""

import os
import time
import psutil
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional


class SystemCollector:
    """系统数据收集器"""
    
    def __init__(self):
        self.system_info = self._get_static_system_info()
    
    def _get_static_system_info(self) -> Dict[str, Any]:
        """获取静态系统信息"""
        try:
            return {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'boot_time': psutil.boot_time()
            }
        except Exception as e:
            print(f"获取静态系统信息时出错: {e}")
            return {}
    
    def collect_cpu_info(self) -> Dict[str, Any]:
        """收集CPU信息"""
        try:
            cpu_times = psutil.cpu_times()
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            return {
                'timestamp': datetime.now(),
                'cpu_percent_total': psutil.cpu_percent(interval=0.1),
                'cpu_percent_per_core': cpu_percent,
                'cpu_times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle,
                    'nice': getattr(cpu_times, 'nice', 0),
                    'iowait': getattr(cpu_times, 'iowait', 0),
                    'irq': getattr(cpu_times, 'irq', 0),
                    'softirq': getattr(cpu_times, 'softirq', 0),
                    'steal': getattr(cpu_times, 'steal', 0),
                    'guest': getattr(cpu_times, 'guest', 0),
                    'guest_nice': getattr(cpu_times, 'guest_nice', 0)
                },
                'load_average': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                },
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True)
            }
        except Exception as e:
            print(f"收集CPU信息时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_memory_info(self) -> Dict[str, Any]:
        """收集内存信息"""
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                'timestamp': datetime.now(),
                'virtual_memory': {
                    'total': virtual_memory.total,
                    'available': virtual_memory.available,
                    'used': virtual_memory.used,
                    'free': virtual_memory.free,
                    'percent': virtual_memory.percent,
                    'active': getattr(virtual_memory, 'active', 0),
                    'inactive': getattr(virtual_memory, 'inactive', 0),
                    'buffers': getattr(virtual_memory, 'buffers', 0),
                    'cached': getattr(virtual_memory, 'cached', 0),
                    'shared': getattr(virtual_memory, 'shared', 0)
                },
                'swap_memory': {
                    'total': swap_memory.total,
                    'used': swap_memory.used,
                    'free': swap_memory.free,
                    'percent': swap_memory.percent,
                    'sin': swap_memory.sin,
                    'sout': swap_memory.sout
                }
            }
        except Exception as e:
            print(f"收集内存信息时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_disk_info(self) -> Dict[str, Any]:
        """收集磁盘信息"""
        try:
            disk_partitions = psutil.disk_partitions()
            disk_usage = {}
            disk_io = psutil.disk_io_counters()
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    }
                except PermissionError:
                    continue
            
            return {
                'timestamp': datetime.now(),
                'disk_usage': disk_usage,
                'disk_io': {
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_time': disk_io.read_time if disk_io else 0,
                    'write_time': disk_io.write_time if disk_io else 0
                } if disk_io else {}
            }
        except Exception as e:
            print(f"收集磁盘信息时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_network_info(self) -> Dict[str, Any]:
        """收集网络信息"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            return {
                'timestamp': datetime.now(),
                'network_io': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errin': net_io.errin,
                    'errout': net_io.errout,
                    'dropin': net_io.dropin,
                    'dropout': net_io.dropout
                },
                'connections_count': net_connections
            }
        except Exception as e:
            print(f"收集网络信息时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_process_info(self, top_n: int = 20) -> Dict[str, Any]:
        """收集进程信息"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'username', 'create_time',
                                           'ppid', 'cmdline']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] is not None:
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_percent': pinfo['cpu_percent'] or 0,
                            'memory_percent': pinfo['memory_percent'] or 0,
                            'memory_rss': pinfo['memory_info'].rss if pinfo['memory_info'] else 0,
                            'memory_vms': pinfo['memory_info'].vms if pinfo['memory_info'] else 0,
                            'status': pinfo['status'],
                            'username': pinfo['username'] or 'unknown',
                            'create_time': pinfo['create_time'],
                            'ppid': pinfo['ppid'],
                            'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'timestamp': datetime.now(),
                'total_processes': len(processes),
                'top_processes': processes[:top_n],
                'all_processes': processes
            }
        except Exception as e:
            print(f"收集进程信息时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_system_summary(self) -> Dict[str, Any]:
        """收集系统概览信息"""
        try:
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            users = psutil.users()
            
            return {
                'timestamp': datetime.now(),
                'uptime': uptime.total_seconds(),
                'uptime_formatted': str(uptime),
                'users_count': len(users),
                'users': [{'name': u.name, 'terminal': u.terminal, 'host': u.host, 
                          'started': u.started} for u in users]
            }
        except Exception as e:
            print(f"收集系统概览时出错: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def collect_all(self, top_processes: int = 20) -> Dict[str, Any]:
        """收集所有系统信息"""
        return {
            'timestamp': datetime.now(),
            'system_info': self.system_info,
            'cpu': self.collect_cpu_info(),
            'memory': self.collect_memory_info(),
            'disk': self.collect_disk_info(),
            'network': self.collect_network_info(),
            'processes': self.collect_process_info(top_processes),
            'summary': self.collect_system_summary()
        } 