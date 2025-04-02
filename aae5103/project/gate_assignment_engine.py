#!/usr/bin/env python3
"""
实时航班登机口管理系统 - 核心分配引擎

本模块实现了航班登机口分配系统的核心算法和数据处理功能。主要功能包括：
1. 航班数据的加载和预处理
2. 登机口分配状态的获取和转换
3. 基于约束规划的登机口重新分配算法

核心算法使用Google OR-Tools的CP-SAT求解器实现，通过设置约束条件（如时间冲突、登机口可用性）
和优化目标（最小化航班与原定登机口之间的距离），生成最优的登机口分配方案。

作者: AAE5103课程项目团队
版本: 1.0.0
"""

# 标准库导入
import os
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# 第三方库导入
import pandas as pd
import numpy as np
from ortools.sat.python import cp_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gate_assignment.log')
    ]
)
logger = logging.getLogger(__name__)

# 常量定义
BUFFER_TIME = 30  # 航班之间的最小间隔时间（分钟）
MAX_SOLVER_TIME = 60.0  # 求解器最大运行时间（秒）
FLIGHT_OCCUPATION_BEFORE = 30  # 航班在起飞前占用登机口的时间（分钟）
FLIGHT_OCCUPATION_AFTER = 30  # 航班在起飞后占用登机口的时间（分钟）

# 全局变量存储最新的航班数据和分配结果
_latest_flights_df = None  # 类型: Optional[pd.DataFrame]
_latest_assignment = None  # 类型: Optional[List[Dict[str, Any]]]

def time_to_minutes(time_str: str) -> int:
    """
    将时间字符串转换为分钟数
    
    参数:
        time_str: 时间字符串，格式为"HH:MM"
        
    返回:
        int: 从0点开始计算的分钟数
        
    示例:
        >>> time_to_minutes("01:30")
        90
    """
    try:
        hours, minutes = time_str.split(':')
        return int(hours) * 60 + int(minutes)
    except (ValueError, AttributeError) as e:
        logger.error(f"时间格式错误: {time_str}, 错误: {e}")
        raise ValueError(f"无效的时间格式: {time_str}, 应为'HH:MM'") from e

def get_data_path(relative_path: str) -> str:
    """
    获取数据文件的绝对路径
    
    系统会按照以下顺序查找数据文件:
    1. 项目的data目录
    2. 预定义的绝对路径
    3. 相对于工作目录的路径
    
    参数:
        relative_path: 数据文件的相对路径
        
    返回:
        str: 数据文件的绝对路径
        
    异常:
        FileNotFoundError: 如果找不到数据文件
    """
    # 预定义的绝对路径
    abs_paths = {
        'aae5103/flight_data_new/flight.xlsx': '/Users/qianjincheng/Documents/python/aae5103/flight_data_new/flight.xlsx',
        'aae5103/flight_data_new/distance.xlsx': '/Users/qianjincheng/Documents/python/aae5103/flight_data_new/distance.xlsx'
    }
    
    # 获取文件名
    file_name = os.path.basename(relative_path)
    
    # 1. 首先检查项目数据目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_data_path = os.path.join(script_dir, 'data', file_name)
    
    if os.path.exists(project_data_path):
        logger.info(f"在项目数据目录找到文件: {project_data_path}")
        return project_data_path
    
    # 2. 检查预定义的绝对路径
    if relative_path in abs_paths:
        full_path = abs_paths[relative_path]
        if os.path.exists(full_path):
            logger.info(f"使用预定义绝对路径: {full_path}")
            return full_path
    
    # 3. 尝试其他可能的路径
    # 构建基于工作目录的路径
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(base_dir, relative_path)
    logger.info(f"尝试路径: base_dir={base_dir}, relative_path={relative_path}, full_path={full_path}")
    
    # 如果该路径存在，返回
    if os.path.exists(full_path):
        return full_path
    
    # 尝试备选路径列表
    possible_paths = [
        relative_path,  # 纯相对路径
        os.path.join(os.getcwd(), relative_path),  # 当前工作目录
    ]
    
    for path in possible_paths:
        logger.info(f"尝试备选路径: {path}")
        if os.path.exists(path):
            logger.info(f"找到有效路径: {path}")
            return path
    
    # 如果所有尝试都失败，记录错误并抛出异常
    error_msg = f"找不到数据文件: {relative_path}，工作目录: {os.getcwd()}"
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

def load_current_flights() -> pd.DataFrame:
    """
    加载当前航班数据
    
    该函数首先检查是否有最新的航班分配数据，如果有则直接使用。
    否则从文件加载原始数据，并进行预处理（提取起飞时间、计算占用时间等）。
    
    返回:
        pd.DataFrame: 包含航班信息的DataFrame，每行代表一个航班，列包括:
            - no: 航班号
            - time: 计划时间
            - status: 航班状态
            - gate: 分配的登机口
            - coordinate: 坐标信息
            - deptime: 提取的起飞时间
            - start: 开始占用登机口的时间（以分钟为单位）
            - end: 结束占用登机口的时间（以分钟为单位）
            
    异常:
        FileNotFoundError: 如果找不到航班数据文件
        Exception: 如果加载或处理过程中发生其他错误
    """
    global _latest_flights_df
    try:
        # 1. 如果有最新的分配结果，优先使用它
        if _latest_flights_df is not None:
            logger.debug("使用最新的航班分配数据")
            return _latest_flights_df.copy()
        
        # 2. 否则从文件加载原始数据
        flight_path = get_data_path('aae5103/flight_data_new/flight.xlsx')
        
        # 3. 如果路径不存在，尝试几种不同的路径
        if not os.path.exists(flight_path):
            possible_paths = [
                'aae5103/flight_data_new/flight.xlsx',  # 相对路径
                '/Users/qianjincheng/Documents/python/aae5103/flight_data_new/flight.xlsx',  # 绝对路径
                os.path.join(os.getcwd(), 'aae5103/flight_data_new/flight.xlsx'),  # 当前工作目录
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'flight.xlsx')  # 项目data目录
            ]
            
            for path in possible_paths:
                logger.debug(f"尝试备选路径: {path}")
                if os.path.exists(path):
                    flight_path = path
                    logger.info(f"找到有效路径: {flight_path}")
                    break
        
        logger.info(f"加载航班数据文件: {flight_path}")
        
        if not os.path.exists(flight_path):
            error_msg = f"航班数据文件不存在: {flight_path}，工作目录: {os.getcwd()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # 4. 从Excel文件加载数据
        flights_df = pd.read_excel(flight_path)
        record_count = len(flights_df)
        logger.info(f"航班数据加载成功，共{record_count}条记录")
        
        if record_count == 0:
            logger.warning("航班数据文件中没有记录")
            return flights_df
        
        # 5. 数据预处理
        # 从status列提取起飞时间
        def extract_departure_time(status: str) -> str:
            try:
                return status.split(' ')[1]
            except (IndexError, AttributeError) as e:
                logger.warning(f"无法从状态中提取起飞时间: {status}, 错误: {e}")
                return "00:00"  # 提供默认值以避免程序崩溃
        
        # 添加deptime列
        flights_df['deptime'] = flights_df['status'].apply(extract_departure_time)
        
        # 计算占用时间
        flights_df['start'] = flights_df['deptime'].apply(time_to_minutes) - FLIGHT_OCCUPATION_BEFORE
        flights_df['end'] = flights_df['deptime'].apply(time_to_minutes) + FLIGHT_OCCUPATION_AFTER
        
        # 6. 保存为最新数据
        _latest_flights_df = flights_df.copy()
        
        return flights_df
    except FileNotFoundError as e:
        # 传递文件相关的特定异常
        logger.error(f"找不到航班数据文件: {str(e)}")
        raise
    except Exception as e:
        # 处理其他所有异常
        error_msg = f"加载航班数据失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise Exception(error_msg) from e

def get_current_flights() -> Dict[str, Any]:
    """
    获取当前航班和登机口信息，用于API返回
    
    该函数加载当前航班数据和距离矩阵，然后将航班数据转换为适合API返回的格式。
    如果存在最新的分配结果，会更新航班的登机口信息。
    
    返回:
        Dict[str, Any]: 包含两个键的字典:
            - flights: 航班信息列表，每个航班为一个字典，包含no, time, deptime, gate, coordinate等字段
            - gates: 所有可用登机口的名称列表
    
    异常:
        FileNotFoundError: 如果找不到必要的数据文件
        Exception: 如果处理过程中发生其他错误
    """
    global _latest_assignment
    
    try:
        # 1. 加载航班数据
        flights_df = load_current_flights()
        
        # 2. 加载距离矩阵以获取登机口信息
        distance_path = get_data_path('aae5103/flight_data_new/distance.xlsx')
        
        # 如果路径不存在，尝试备选路径
        if not os.path.exists(distance_path):
            possible_paths = [
                'aae5103/flight_data_new/distance.xlsx',  # 相对路径
                '/Users/qianjincheng/Documents/python/aae5103/flight_data_new/distance.xlsx',  # 绝对路径
                os.path.join(os.getcwd(), 'aae5103/flight_data_new/distance.xlsx'),  # 当前工作目录
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'distance.xlsx')  # 项目data目录
            ]
            
            for path in possible_paths:
                logger.debug(f"尝试备选路径: {path}")
                if os.path.exists(path):
                    distance_path = path
                    logger.info(f"找到有效路径: {distance_path}")
                    break
            
        logger.info(f"加载距离矩阵文件: {distance_path}")
        
        if not os.path.exists(distance_path):
            error_msg = f"距离矩阵文件不存在: {distance_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # 3. 读取距离矩阵，提取登机口名称
        distance_df = pd.read_excel(distance_path, index_col=0)
        gate_names = distance_df.index.tolist()
        logger.info(f"距离矩阵加载成功，共{len(gate_names)}个登机口")
        
        # 4. 将航班数据转换为JSON友好格式
        flights_list = []
        for _, flight in flights_df.iterrows():
            # 确保所有时间类型数据都转换为字符串格式
            flights_list.append({
                'no': flight['no'],
                'time': str(flight['time']) if not isinstance(flight['time'], str) else flight['time'],
                'deptime': str(flight['deptime']) if not isinstance(flight['deptime'], str) else flight['deptime'],
                'gate': flight['gate'],
                'coordinate': flight['coordinate']
            })
        
        # 5. 构建结果字典
        result = {
            'flights': flights_list,
            'gates': gate_names
        }
        
        # 6. 如果有最新的分配结果，更新航班的登机口信息
        if _latest_assignment is not None:
            update_count = 0
            for flight in result['flights']:
                for assignment in _latest_assignment:
                    if flight['no'] == assignment['flight']:
                        flight['gate'] = assignment['new_gate']
                        update_count += 1
            logger.debug(f"根据最新分配结果更新了{update_count}个航班的登机口信息")
        
        return result
    except FileNotFoundError as e:
        # 传递文件相关的特定异常
        logger.error(f"找不到数据文件: {str(e)}")
        raise
    except Exception as e:
        # 处理其他所有异常
        error_msg = f"获取航班信息失败: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise Exception(error_msg) from e

def check_time_overlap(
    flight1_start: int, 
    flight1_end: int, 
    flight2_start: int, 
    flight2_end: int, 
    buffer_time: int
) -> Tuple[bool, Optional[int]]:
    """
    检查两个时间区间是否重叠或间隔不足
    
    参数:
        flight1_start: 第一个航班开始时间（分钟）
        flight1_end: 第一个航班结束时间（分钟）
        flight2_start: 第二个航班开始时间（分钟）
        flight2_end: 第二个航班结束时间（分钟）
        buffer_time: 所需的最小间隔时间（分钟）
        
    返回:
        Tuple[bool, Optional[int]]: 
            - 第一个元素：是否有重叠或间隔不足
            - 第二个元素：如有重叠，返回重叠量（分钟）；如间隔不足，返回间隔时间；否则返回None
    """
    # 如果航班1在航班2之前
    if flight1_end <= flight2_start:
        interval = flight2_start - flight1_end
        if interval < buffer_time:
            return True, interval
        return False, None
        
    # 如果航班2在航班1之前
    elif flight2_end <= flight1_start:
        interval = flight1_start - flight2_end
        if interval < buffer_time:
            return True, interval
        return False, None
        
    # 如果两个航班时间有重叠
    else:
        overlap = min(flight1_end, flight2_end) - max(flight1_start, flight2_start)
        return True, overlap

def reassign_gates(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据突发事件重新分配登机口
    
    该函数实现了核心的登机口分配算法。它通过约束规划模型解决登机口分配问题，
    考虑时间冲突约束、登机口可用性约束，并最小化航班与原定登机口之间的距离。
    
    处理流程:
    1. 加载航班数据和距离矩阵
    2. 根据突发事件（登机口关闭、航班延误）更新约束条件
    3. 预处理，检查初始数据中的冲突
    4. 构建约束规划模型，包括决策变量、约束条件和目标函数
    5. 求解模型并返回分配结果
    
    参数:
        event_data: 包含突发事件信息的字典，格式如下:
            {
                'closed_gates': ['G12', 'B3'],  # 关闭的登机口列表
                'delayed_flights': [            # 延误航班列表
                    {'no': 'CX 675', 'new_time': '14:30'}
                ],
                '_force_reassign': True         # 可选，强制重新分配标志
            }
    
    返回:
        Dict[str, Any]: 包含分配结果的字典，格式如下:
            {
                'status': 'success' | 'failed',  # 分配状态
                'message': '...',                # 如果失败，包含错误信息
                'assignment': [                  # 分配结果列表
                    {
                        'flight': 'CX 675',      # 航班号
                        'original_gate': 'G12',  # 原登机口
                        'new_gate': 'G15',       # 新登机口
                        'time': '14:30'          # 起飞时间
                    },
                    ...
                ]
            }
    
    异常:
        所有异常都会被捕获并返回错误状态
    """
    global _latest_flights_df, _latest_assignment
    
    try:
        logger.info(f"开始处理重新分配请求: {json.dumps(event_data)}")
        
        # 1. 加载当前航班数据
        flights_df = load_current_flights()
        
        # 2. 读取距离矩阵
        distance_path = get_data_path('aae5103/flight_data_new/distance.xlsx')
        
        # 如果路径不存在，尝试其他路径
        if not os.path.exists(distance_path):
            possible_paths = [
                'aae5103/flight_data_new/distance.xlsx',  # 相对路径
                '/Users/qianjincheng/Documents/python/aae5103/flight_data_new/distance.xlsx',  # 绝对路径
                os.path.join(os.getcwd(), 'aae5103/flight_data_new/distance.xlsx'),  # 当前工作目录
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'distance.xlsx')  # 项目data目录
            ]
            
            for path in possible_paths:
                logger.debug(f"尝试备选路径: {path}")
                if os.path.exists(path):
                    distance_path = path
                    logger.info(f"找到有效路径: {distance_path}")
                    break
            
        logger.info(f"使用距离矩阵文件: {distance_path}")
        
        if not os.path.exists(distance_path):
            error_msg = f"距离矩阵文件不存在: {distance_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # 3. 加载距离矩阵
        distance_df = pd.read_excel(distance_path, index_col=0)
        gate_names = distance_df.index.tolist()
        num_gates = len(gate_names)
        gate_name_to_idx = {name: idx for idx, name in enumerate(gate_names)}
        
        # 4. 处理原计划登机口索引
        flights_df['original_gate_idx'] = flights_df['gate'].map(gate_name_to_idx)
        
        # 5. 处理突发事件：登机口关闭
        unavailable_gates = []
        if 'closed_gates' in event_data and event_data['closed_gates']:
            # 将某些登机口标记为不可用
            unavailable_gates = event_data['closed_gates']
            logger.info(f"处理关闭的登机口: {unavailable_gates}")
            
            # 确保这些登机口存在于数据中
            valid_gates = []
            for gate in unavailable_gates:
                if gate in gate_name_to_idx:
                    valid_gates.append(gate)
                else:
                    logger.warning(f"登机口 {gate} 不在有效登机口列表中")
            unavailable_gates = valid_gates
            
            if not valid_gates and unavailable_gates:
                logger.warning(f"提供的所有登机口 {unavailable_gates} 都无效，无法进行关闭操作")
        
        # 6. 处理突发事件：航班延误
        if 'delayed_flights' in event_data and event_data['delayed_flights']:
            delayed_count = 0
            # 更新延误航班的时间
            for flight in event_data['delayed_flights']:
                logger.info(f"处理延误航班: {flight}")
                idx = flights_df[flights_df['no'] == flight['no']].index
                if not idx.empty:
                    # 获取原来的时间用于日志记录
                    old_deptime = flights_df.loc[idx, 'deptime'].iloc[0]
                    
                    # 更新deptime, time和status字段
                    flights_df.loc[idx, 'deptime'] = flight['new_time']
                    flights_df.loc[idx, 'time'] = flight['new_time']
                    # 更新status字段，确保一致性
                    flights_df.loc[idx, 'status'] = flights_df.loc[idx, 'status'].str.replace(old_deptime, flight['new_time'])
                    
                    # 重新计算开始和结束时间
                    # 每个航班占用登机口的时间为起飞前30分钟到起飞后30分钟
                    new_start = time_to_minutes(flight['new_time']) - FLIGHT_OCCUPATION_BEFORE
                    new_end = time_to_minutes(flight['new_time']) + FLIGHT_OCCUPATION_AFTER
                    flights_df.loc[idx, 'start'] = new_start
                    flights_df.loc[idx, 'end'] = new_end
                    logger.info(f"航班 {flight['no']} 时间从 {old_deptime} 更新为 {flight['new_time']} (占用时间段:{new_start}-{new_end})")
                    delayed_count += 1
                else:
                    logger.warning(f"找不到航班: {flight['no']}")
            
            logger.info(f"共更新了 {delayed_count} 个延误航班的时间")
        
        # 7. 构建距离矩阵并将浮点数转换为整数
        # 转换为整数是为了提高CP-SAT求解器的数值稳定性
        distance_matrix = []
        for row in distance_df.values:
            int_row = [int(d * 100) for d in row]  # 将浮点距离乘以100并转换为整数
            distance_matrix.append(int_row)
        
        # 8. 预处理：检查初始数据中的时间冲突
        # 将航班按登机口分组，检查同一登机口的航班是否有时间冲突
        gate_conflicts = {}
        
        for gate in gate_names:
            gate_flights = flights_df[flights_df['gate'] == gate]
            if len(gate_flights) > 1:
                # 查找该登机口内的时间冲突
                flights_at_gate = gate_flights.to_dict('records')
                conflicts = []
                
                for i in range(len(flights_at_gate)):
                    for j in range(i + 1, len(flights_at_gate)):
                        flight_i = flights_at_gate[i]
                        flight_j = flights_at_gate[j]
                        
                        # 检查时间是否重叠或间隔不足
                        time_overlap, overlap_value = check_time_overlap(
                            flight_i['start'], flight_i['end'],
                            flight_j['start'], flight_j['end'],
                            BUFFER_TIME
                        )
                        
                        if time_overlap:
                            logger.warning(
                                f"初始数据中发现时间冲突：登机口 {gate} 的航班 "
                                f"{flight_i['no']}({flight_i['deptime']}) 和 "
                                f"{flight_j['no']}({flight_j['deptime']})"
                            )
                            conflicts.append((flight_i['no'], flight_j['no']))
                
                if conflicts:
                    gate_conflicts[gate] = conflicts
        
        # 9. 处理初始数据中的冲突
        if gate_conflicts:
            conflict_details = json.dumps(gate_conflicts)
            logger.warning(f"发现初始数据中的时间冲突：{conflict_details}")
            
            # 如果不是显式要求关闭登机口，但有冲突，强制进行重新分配
            if 'closed_gates' not in event_data or not event_data['closed_gates']:
                logger.info("没有指定关闭登机口，但有时间冲突，将进行重新分配")
                
                # 将所有有冲突的登机口标记为需要重新分配
                for gate in gate_conflicts:
                    if gate not in unavailable_gates:
                        unavailable_gates.append(gate)
                
                logger.info(f"将有冲突的登机口标记为需要重新分配：{unavailable_gates}")
        
        # 10. 特殊情况处理：检查关闭的登机口是否有安排的航班
        flights_to_reassign = []
        for gate in unavailable_gates:
            gate_flights = flights_df[flights_df['gate'] == gate]
            if not gate_flights.empty:
                flight_list = gate_flights['no'].tolist()
                logger.info(f"登机口 {gate} 关闭，需要重新分配以下航班: {flight_list}")
                flights_to_reassign.extend(flight_list)
        
        # 11. 如果没有需要处理的事件，或无航班需要重新分配，返回原始分配
        force_reassign = '_force_reassign' in event_data and event_data['_force_reassign']
        
        if ((not unavailable_gates and not event_data.get('delayed_flights')) or 
            (unavailable_gates and not flights_to_reassign and not force_reassign)):
            
            logger.info("没有需要处理的事件或关闭登机口不影响任何航班，返回原始分配")
            assignment = []
            for _, flight in flights_df.iterrows():
                assignment.append({
                    'flight': flight['no'],
                    'original_gate': flight['gate'],
                    'new_gate': flight['gate'],
                    'time': str(flight['deptime']) if not isinstance(flight['deptime'], str) else flight['deptime']
                })
            
            return {'status': 'success', 'assignment': assignment}
        
        # 12. 创建约束规划模型
        model = cp_model.CpModel()
        num_flights = len(flights_df)
        logger.info(f"创建约束规划模型: {num_flights}个航班, {num_gates}个登机口")
        
        # 13. 定义决策变量：每个航班分配的登机口索引
        gates = [model.NewIntVar(0, num_gates-1, f'gate_{i}') for i in range(num_flights)]
        
        # 14. 创建二维布尔变量数组，表示航班i是否分配到登机口j
        assigned = {}
        for i in range(num_flights):
            for j in range(num_gates):
                assigned[(i, j)] = model.NewBoolVar(f'assigned_{i}_{j}')
                # 如果gates[i] == j，则assigned[(i, j)] = True
                model.Add(gates[i] == j).OnlyEnforceIf(assigned[(i, j)])
                model.Add(gates[i] != j).OnlyEnforceIf(assigned[(i, j)].Not())
        
        # 15. 添加约束1：每个航班必须分配到一个登机口
        for i in range(num_flights):
            model.Add(sum(assigned[(i, j)] for j in range(num_gates)) == 1)
        
        # 16. 添加约束2：检查时间重叠并添加约束
        time_conflicts = 0
        for j in range(num_gates):  # 对每个登机口
            for i in range(num_flights):  # 对每对航班
                for k in range(i + 1, num_flights):
                    # 获取航班时间
                    flight_i_start = flights_df.iloc[i]['start']
                    flight_i_end = flights_df.iloc[i]['end']
                    flight_k_start = flights_df.iloc[k]['start']
                    flight_k_end = flights_df.iloc[k]['end']
                    
                    # 航班编号
                    flight_i_no = flights_df.iloc[i]['no']
                    flight_k_no = flights_df.iloc[k]['no']
                    
                    # 判断是否重叠或间隔不足
                    time_overlap, overlap_value = check_time_overlap(
                        flight_i_start, flight_i_end,
                        flight_k_start, flight_k_end,
                        BUFFER_TIME
                    )
                    
                    if time_overlap:
                        # 记录详细的重叠信息
                        if flight_i_end <= flight_k_start or flight_k_end <= flight_i_start:
                            logger.info(
                                f"航班 {flight_i_no} 和 {flight_k_no} 间隔 {overlap_value} 分钟，"
                                f"小于所需的 {BUFFER_TIME} 分钟"
                            )
                        else:
                            logger.info(f"航班 {flight_i_no} 和 {flight_k_no}: 时间重叠 {overlap_value} 分钟")
                        
                        # 如果有重叠或间隔不足，这两个航班不能同时分配到同一个登机口j
                        model.Add(assigned[(i, j)] + assigned[(k, j)] <= 1)
                        time_conflicts += 1
        
        logger.info(f"共添加了 {time_conflicts} 个时间冲突约束")
        
        # 17. 添加约束3：处理不可用登机口
        if unavailable_gates:
            constraint_count = 0
            for gate_name in unavailable_gates:
                if gate_name in gate_name_to_idx:
                    j = gate_name_to_idx[gate_name]
                    # 添加约束：所有航班都不能分配到这个登机口
                    for i in range(num_flights):
                        flight_no = flights_df.iloc[i]['no']
                        model.Add(assigned[(i, j)] == 0)
                        logger.debug(f"添加约束：航班 {flight_no} 不能分配到关闭的登机口 {gate_name}")
                        constraint_count += 1
                else:
                    logger.warning(f"无效的登机口名称：{gate_name}，忽略该约束")
            logger.info(f"共添加了 {constraint_count} 个登机口不可用约束")
        
        # 18. 构建目标函数：最小化总距离
        objective_terms = []
        for i in range(num_flights):
            flight_no = flights_df.iloc[i]['no']
            original_gate = flights_df.loc[i, 'original_gate_idx']
            
            for j in range(num_gates):
                gate_name = gate_names[j]
                # 如果航班i被分配到登机口j，添加相应的距离
                distance = distance_matrix[original_gate][j]
                objective_terms.append(distance * assigned[(i, j)])
                
                logger.debug(
                    f"如果航班 {flight_no} 从 {flights_df.loc[i, 'gate']} 分配到 {gate_name}, "
                    f"增加距离 {distance/100:.2f}"
                )
        
        # 构建目标函数
        model.Minimize(sum(objective_terms))
        
        # 19. 求解模型
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = MAX_SOLVER_TIME  # 设置最大求解时间
        
        logger.info(f"开始求解模型，最大求解时间: {MAX_SOLVER_TIME}秒...")
        status = solver.Solve(model)
        
        # 记录求解结果
        status_name = solver.StatusName(status)
        objective_value = solver.ObjectiveValue() if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else None
        logger.info(f"模型求解完成，状态: {status_name}, 目标值: {objective_value}")
        
        # 20. 返回新的分配方案
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            new_assignment = []
            gate_changes = {}  # 用于追踪从原登机口到新登机口的变化
            
            # 更新航班的登机口分配
            for i in range(len(flights_df)):
                flight = flights_df.iloc[i]
                flight_no = flight['no']
                original_gate = flight['gate']
                
                # 找到分配的登机口
                assigned_gate = None
                for j in range(num_gates):
                    if solver.Value(assigned[(i, j)]) == 1:
                        assigned_gate = gate_names[j]
                        break
                
                if assigned_gate is None:
                    error_msg = f"航班 {flight_no} 没有被分配到任何登机口"
                    logger.error(error_msg)
                    continue
                
                # 检查分配的登机口是否在不可用列表中
                if assigned_gate in unavailable_gates:
                    error_msg = f"错误：航班 {flight_no} 被分配到关闭的登机口 {assigned_gate}"
                    logger.error(error_msg)
                    # 尝试寻找一个可用的替代登机口（简单贪心策略）
                    alternative_found = False
                    for alt_gate in gate_names:
                        if alt_gate not in unavailable_gates:
                            # 简单检查：确保没有时间冲突
                            conflict_exists = False
                            for _, other_flight in flights_df.iterrows():
                                if other_flight['gate'] == alt_gate and other_flight['no'] != flight_no:
                                    # 检查时间重叠
                                    time_overlap, _ = check_time_overlap(
                                        flight['start'], flight['end'],
                                        other_flight['start'], other_flight['end'],
                                        BUFFER_TIME
                                    )
                                    if time_overlap:
                                        conflict_exists = True
                                        break
                            
                            if not conflict_exists:
                                assigned_gate = alt_gate
                                logger.info(f"手动修正：将航班 {flight_no} 从关闭的登机口 {original_gate} 重新分配到 {assigned_gate}")
                                alternative_found = True
                                break
                    
                    if not alternative_found:
                        logger.error(f"无法为航班 {flight_no} 找到替代登机口，保留在 {assigned_gate}（注意：这是一个错误的分配）")
                
                # 记录变化
                if original_gate != assigned_gate:
                    gate_changes[flight_no] = {
                        'from': original_gate,
                        'to': assigned_gate
                    }
                
                # 更新DataFrame中的登机口信息
                flights_df.at[i, 'gate'] = assigned_gate
                
                # 添加到结果列表
                flight_time = str(flight['deptime']) if not isinstance(flight['deptime'], str) else flight['deptime']
                new_assignment.append({
                    'flight': flight_no,
                    'original_gate': original_gate,
                    'new_gate': assigned_gate,
                    'time': flight_time
                })
            
            # 21. 检查是否有任何变化并保存最新结果
            if gate_changes:
                # 保存最新的分配结果
                _latest_flights_df = flights_df.copy()
                _latest_assignment = new_assignment
                
                # 记录变化详情
                logger.info(f"出现登机口变化：{len(gate_changes)}个航班更新了登机口")
                for flight, change in gate_changes.items():
                    logger.info(f"航班 {flight}: {change['from']} → {change['to']}")
            else:
                logger.info("重新分配完成，但没有航班需要更改登机口")
            
            logger.info(f"成功生成分配方案，共{len(new_assignment)}个航班")
            return {
                'status': 'success', 
                'assignment': new_assignment,
                'objective_value': float(objective_value) / 100 if objective_value else None
            }
        else:
            error_msg = f"无法找到可行解，状态: {status_name}"
            logger.error(error_msg)
            return {'status': 'failed', 'message': error_msg}
            
    except FileNotFoundError as e:
        error_msg = f"找不到必要的数据文件: {str(e)}"
        logger.error(error_msg)
        return {'status': 'failed', 'message': error_msg}
        
    except Exception as e:
        error_msg = f"重新分配登机口过程中发生错误: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {'status': 'failed', 'message': error_msg} 