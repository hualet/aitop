# AITop - 智能系统监控工具

AITop是一个智能系统监控工具，结合了传统`top`命令的实时性和AI分析的智能性。它提供类似top的命令行界面来实时监控系统进程，并在收集一段时间数据后生成智能化的HTML5分析报告。

## 项目概述

### 核心使命
创建一个智能系统监控工具，具备以下特性：
- **实时进程监控**：类似top命令的界面，实时显示系统前20个进程的CPU、内存占用情况
- **定时刷新**：每秒更新一次进程信息，提供流畅的实时体验
- **数据收集**：在后台持续收集系统资源使用情况和系统日志
- **AI智能分析**：收集一段时间（如2分钟）后，AI分析系统性能和日志模式
- **现代化报告**：生成包含分析结果和建议的HTML5网页报告

### 目标用户
- 系统管理员
- DevOps工程师  
- 需要调试性能问题的开发者
- 任何需要智能系统监控的用户

## 核心功能设计

### 1. 类Top命令行界面
```
AITop - 智能系统监控 v1.0.0                    更新时间: 14:30:25
==================================================================
系统概览: CPU: 45.2% | 内存: 67.8% | 负载: 2.34 | 运行时间: 2天3小时

PID    进程名称              CPU%   内存%   内存使用    状态    用户
------------------------------------------------------------------
1234   chrome               15.2    8.4     2.1GB      运行    user
5678   python               12.8    4.2     1.2GB      运行    user
9012   node                 8.9     3.1     890MB      运行    user
3456   firefox              6.7     5.8     1.8GB      运行    user
7890   vscode               4.2     2.9     780MB      运行    user
2345   docker               3.8     1.2     340MB      运行    root
6789   mysql                2.1     6.4     2.0GB      运行    mysql
...
==================================================================
数据收集中... (已收集 45秒/120秒) | 按 'q' 退出 | 按 'r' 生成报告
```

### 2. 数据收集模块
- **进程信息**：PID、进程名、CPU使用率、内存使用率、状态、用户
- **系统资源**：CPU总使用率、内存使用情况、磁盘I/O、网络流量
- **系统日志**：通过journalctl收集重要系统事件和错误日志
- **历史数据**：保存时间序列数据用于趋势分析

### 3. AI分析引擎
- **性能异常检测**：识别CPU、内存使用异常模式
- **进程行为分析**：分析进程资源消耗趋势
- **日志智能分析**：从系统日志中提取关键事件和错误模式
- **相关性分析**：关联系统指标变化与日志事件
- **预测性建议**：基于历史数据预测潜在问题

### 4. HTML5报告生成
生成包含以下内容的现代化网页报告：
- **执行摘要**：系统健康状况概览
- **性能分析**：CPU、内存使用趋势图表
- **进程分析**：资源消耗排行和异常进程识别
- **日志分析**：重要事件时间线和错误统计
- **AI洞察**：智能分析结果和优化建议
- **交互式图表**：可缩放的时间序列图表

## 技术架构

### 系统组件
1. **命令行界面** (`src/aitop/cli.py`)
   - 实时进程显示
   - 用户交互处理
   - 状态更新循环

2. **数据收集器** (`src/collector/`)
   - 进程信息收集
   - 系统资源监控
   - 日志数据获取

3. **AI分析器** (`src/analyzer/`)
   - 异常检测算法
   - 模式识别
   - 趋势分析

4. **报告生成器** (`src/reporter/`)
   - HTML模板引擎
   - 图表生成
   - 数据可视化

5. **Web服务器** (`src/web/`)
   - 报告服务
   - 静态资源管理

### 技术栈
- **后端**：Python 3.8+
- **系统监控**：psutil, subprocess
- **AI/ML**：scikit-learn, pandas, numpy
- **数据存储**：SQLite (轻量级时间序列存储)
- **前端**：HTML5, CSS3, JavaScript (Chart.js)
- **模板引擎**：Jinja2

## 用户体验流程

### 基本使用流程
1. **启动监控**：运行 `aitop` 命令
2. **实时观察**：查看类似top的实时进程信息
3. **数据收集**：程序在后台收集系统数据（默认2分钟）
4. **生成报告**：收集完成后自动生成HTML报告，或按'r'手动生成
5. **查看分析**：在浏览器中查看详细的AI分析报告

### 命令行选项
```bash
# 基本使用
aitop

# 指定收集时间
aitop --duration 300  # 收集5分钟数据

# 指定刷新间隔
aitop --refresh 2     # 每2秒刷新一次

# 直接生成报告（不显示实时界面）
aitop --report-only --duration 120

# 指定报告输出路径
aitop --output /path/to/report.html

# 显示更多进程
aitop --top 50        # 显示前50个进程
```

## 开发实现计划

### 第一阶段：核心功能实现
- [x] 基础项目结构
- [ ] 实现类top的命令行界面
- [ ] 进程信息收集和显示
- [ ] 基本的数据存储

### 第二阶段：数据收集和存储
- [ ] 完善系统资源监控
- [ ] 实现日志收集功能
- [ ] 时间序列数据存储
- [ ] 数据清理和管理

### 第三阶段：AI分析集成
- [ ] 异常检测算法
- [ ] 日志分析和模式识别
- [ ] 性能趋势分析
- [ ] 智能建议生成

### 第四阶段：报告生成
- [ ] HTML模板设计
- [ ] 交互式图表实现
- [ ] 报告数据可视化
- [ ] 现代化UI/UX

### 第五阶段：优化和完善
- [ ] 性能优化
- [ ] 错误处理和稳定性
- [ ] 文档完善
- [ ] 测试覆盖

## 配置文件结构

```yaml
# aitop.yaml
display:
  refresh_interval: 1        # 界面刷新间隔（秒）
  top_processes: 20          # 显示的进程数量
  show_threads: false        # 是否显示线程

collection:
  duration: 120              # 数据收集时长（秒）
  sample_interval: 1         # 数据采样间隔（秒）
  include_logs: true         # 是否收集系统日志
  
analysis:
  enabled: true              # 是否启用AI分析
  anomaly_detection: true    # 异常检测
  trend_analysis: true       # 趋势分析
  log_analysis: true         # 日志分析

report:
  auto_generate: true        # 收集完成后自动生成报告
  output_dir: "./reports"    # 报告输出目录
  open_browser: true         # 生成后自动打开浏览器

storage:
  data_dir: "./data"         # 数据存储目录
  retention_days: 7          # 数据保留天数
```

## 报告示例结构

### HTML报告布局
```html
<!DOCTYPE html>
<html>
<head>
    <title>AITop 系统分析报告</title>
    <style>/* 现代化CSS样式 */</style>
</head>
<body>
    <header>
        <h1>系统性能分析报告</h1>
        <div class="report-info">
            <span>分析时间: 2024-01-15 14:30-14:32</span>
            <span>系统: Linux Ubuntu 22.04</span>
        </div>
    </header>
    
    <section class="summary">
        <h2>执行摘要</h2>
        <div class="health-score">系统健康评分: 85/100</div>
        <div class="key-insights">
            <h3>关键发现</h3>
            <ul>
                <li>Chrome进程CPU使用率异常（平均15.2%）</li>
                <li>内存使用率稳定在67%左右</li>
                <li>检测到3个系统错误事件</li>
            </ul>
        </div>
    </section>
    
    <section class="charts">
        <h2>性能趋势</h2>
        <div class="chart-container">
            <canvas id="cpuChart"></canvas>
            <canvas id="memoryChart"></canvas>
        </div>
    </section>
    
    <section class="processes">
        <h2>进程分析</h2>
        <table class="process-table">
            <!-- 进程数据表格 -->
        </table>
    </section>
    
    <section class="logs">
        <h2>日志分析</h2>
        <div class="log-timeline">
            <!-- 日志事件时间线 -->
        </div>
    </section>
    
    <section class="recommendations">
        <h2>AI建议</h2>
        <div class="recommendation-list">
            <!-- AI生成的优化建议 -->
        </div>
    </section>
</body>
</html>
```

## 成功指标

- **用户体验**：启动到显示进程信息 < 2秒
- **系统开销**：自身CPU使用率 < 5%，内存使用 < 100MB
- **数据准确性**：进程信息准确率 > 99%
- **AI分析质量**：异常检测准确率 > 90%
- **报告生成速度**：2分钟数据生成报告 < 10秒

这个重新设计的AITop项目将传统系统监控工具的实时性与现代AI分析能力相结合，为用户提供既直观又智能的系统监控体验。
