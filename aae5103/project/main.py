import pandas as pd
from ortools.sat.python import cp_model
import logging

# 设置日志
logger = logging.getLogger(__name__)

def run_assignment():
    """执行登机口分配算法并输出结果"""
    # 读取航班数据
    flights_df = pd.read_excel('aae5103/flight_data_new/flight.xlsx')
    logger.info(f"航班数据加载成功，共{len(flights_df)}条记录")

    # 时间处理函数
    def time_to_minutes(t):
        return int(t.split(':')[0]) * 60 + int(t.split(':')[1])

    # 从status列提取起飞时间 (格式如 "Dep 00:18")
    def extract_departure_time(status):
        return status.split(' ')[1]

    # 添加deptime列
    flights_df['deptime'] = flights_df['status'].apply(extract_departure_time)

    # 计算占用时间（假设起飞前后各需要30分钟）
    flights_df['start'] = flights_df['deptime'].apply(time_to_minutes) - 30
    flights_df['end'] = flights_df['deptime'].apply(time_to_minutes) + 30

    # 读取距离矩阵
    distance_df = pd.read_excel('aae5103/flight_data_new/distance.xlsx', index_col=0)
    gate_names = distance_df.index.tolist()
    num_gates = len(gate_names)
    logger.info(f"距离矩阵加载成功，共{num_gates}个登机口")
    
    gate_name_to_idx = {name: idx for idx, name in enumerate(gate_names)}

    # 处理原计划登机口索引
    flights_df['original_gate_idx'] = flights_df['gate'].map(gate_name_to_idx)

    # 构建距离矩阵并将浮点数转换为整数（乘以100以保留精度）
    distance_matrix = []
    for row in distance_df.values:
        int_row = [int(d * 100) for d in row]  # 将浮点距离乘以100并转换为整数
        distance_matrix.append(int_row)

    # 创建约束规划模型
    model = cp_model.CpModel()
    num_flights = len(flights_df)
    logger.info(f"创建约束规划模型: {num_flights}个航班, {num_gates}个登机口")

    # 决策变量：每个航班分配的登机口索引
    gates = [model.NewIntVar(0, num_gates-1, f'gate_{i}') for i in range(num_flights)]

    # 约束：同一登机口的航班时间不重叠
    for gate_idx in range(num_gates):
        intervals = []
        for flight_idx in range(num_flights):
            # 创建可选区间变量
            presence = model.NewBoolVar(f'presence_{flight_idx}_{gate_idx}')
            model.Add(gates[flight_idx] == gate_idx).OnlyEnforceIf(presence)
            interval = model.NewOptionalIntervalVar(
                int(flights_df.loc[flight_idx, 'start']),
                int(flights_df.loc[flight_idx, 'end'] - flights_df.loc[flight_idx, 'start']),
                int(flights_df.loc[flight_idx, 'end']),
                presence,
                f'interval_{flight_idx}_{gate_idx}'
            )
            intervals.append(interval)
        model.AddNoOverlap(intervals)

    # 目标函数：最小化总距离
    objective_terms = []
    for flight_idx in range(num_flights):
        original_gate = flights_df.loc[flight_idx, 'original_gate_idx']
        gate_var = gates[flight_idx]
        # 使用Element表达式获取对应距离
        distance = model.NewIntVar(0, 100000, f'distance_{flight_idx}')
        model.AddElement(gate_var, distance_matrix[original_gate], distance)
        objective_terms.append(distance)

    # 使用OR-Tools正确的方式构建目标函数
    objective = 0
    for term in objective_terms:
        objective += term
    model.Minimize(objective)

    # 求解模型
    solver = cp_model.CpSolver()
    logger.info("开始求解模型...")
    status = solver.Solve(model)
    logger.info(f"模型求解完成，状态: {solver.StatusName(status)}")

    # 输出结果
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print(f'Total distance = {solver.ObjectiveValue()}')
        print('\n航班分配方案：')
        for i in range(num_flights):
            original_gate = flights_df.loc[i, 'gate']
            assigned_gate = gate_names[solver.Value(gates[i])]
            print(f'航班 {flights_df.loc[i, "no"]}：'
                f'原计划 {original_gate} → 实际分配 {assigned_gate}')
    else:
        print('未找到可行解')

    # 输出求解统计信息
    print('\n求解统计：')
    print(f'状态: {solver.StatusName(status)}')
    print(f'求解时间: {solver.WallTime()} 秒')
    
    return status == cp_model.OPTIMAL

if __name__ == "__main__":
    # 设置直接运行时的日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_assignment()