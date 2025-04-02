# 项目结构与文件组织

本文档详细说明实时航班登机口管理系统的文件结构和各组件功能。

## 核心文件与目录

```
aae5103/project/
├── README.md             # 项目总体说明与使用指南
├── CONTRIBUTING.md       # 代码贡献指南
├── STRUCTURE.md          # 项目结构文档（本文件）
├── requirements.txt      # 项目依赖列表
├── run.py                # 系统启动脚本
├── app.py                # Web应用服务器
├── gate_assignment_engine.py # 核心算法引擎
├── data/                 # 数据文件目录
│   ├── flight.xlsx       # 航班数据
│   └── distance.xlsx     # 距离矩阵
└── templates/            # Web前端模板
    └── dashboard.html    # 主界面模板
```

## 组件功能说明

### 1. 入口脚本 (`run.py`)

系统主入口，支持两种运行模式：Web界面和命令行界面。
- 配置命令行参数解析
- 设置日志系统
- 检查环境和数据文件
- 根据模式启动相应的应用程序

### 2. Web应用服务器 (`app.py`)

使用Flask框架实现的Web应用，提供以下API端点：
- `GET /`: 返回系统主界面
- `GET /current_assignment`: 获取当前航班与登机口分配状态
- `POST /reassign`: 处理重新分配请求，支持关闭登机口和航班延误
- `GET /health`: 健康检查端点，用于监控系统状态

### 3. 核心算法引擎 (`gate_assignment_engine.py`)

实现登机口分配的核心算法和数据处理功能：
- 数据加载和预处理
- 登机口分配约束规划模型
- 冲突检测与解决
- 优化目标计算

主要函数：
- `load_current_flights()`: 加载当前航班数据
- `get_current_flights()`: 为API提供航班信息
- `reassign_gates()`: 根据突发事件重新分配登机口

### 4. 前端界面 (`templates/dashboard.html`)

基于HTML、CSS和JavaScript（jQuery）的用户界面：
- 实时显示航班和登机口分配状态
- 提供关闭登机口和设置航班延误功能
- 触发重新分配操作并显示结果
- 自动检测并警告时间冲突

### 5. 数据文件 (`data/`)

系统依赖的核心数据文件：
- `flight.xlsx`: 航班信息（航班号、时间、状态、登机口、坐标）
- `distance.xlsx`: 登机口之间的距离矩阵，用于最小化分配变更的成本

## 数据流

1. 用户在Web界面上操作（关闭登机口或设置航班延误）
2. 前端发送请求到服务器的`/reassign`端点
3. 服务器调用`gate_assignment_engine.py`的`reassign_gates()`函数
4. 算法引擎加载数据，构建优化模型，求解最优分配方案
5. 结果返回给前端并更新界面显示

## 设计模式与架构

系统采用经典的三层架构：
- **表现层**：`dashboard.html`提供用户界面
- **业务逻辑层**：`app.py`和`gate_assignment_engine.py`实现业务逻辑
- **数据层**：Excel文件提供数据存储

关键设计决策：
1. 使用Google OR-Tools实现约束规划模型，高效求解复杂分配问题
2. 前端和后端完全解耦，通过REST API进行通信
3. 全局变量`_latest_flights_df`和`_latest_assignment`保存最新分配结果，避免频繁读取文件

## 改进机会

系统潜在的改进方向：
1. 引入数据库替代Excel文件，提高数据管理能力
2. 添加用户认证和权限管理
3. 实现更复杂的优化目标，如考虑旅客连接时间
4. 开发监控仪表板，展示系统性能和分配效率指标 