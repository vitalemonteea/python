import pandas as pd
import re
import os

from datetime import datetime, timedelta

def preprocess_flight_data(df):
    """
    Preprocessed flight data
    df: DataFrame with Date, Time, Status, Gate, NO. columns
    """
    # 1. Extraction of airline codes
    df['Airline'] = df['NO.'].str[:2]
    
    # 2. Processing the Status column
    def parse_status(row):
        if row['Status'] == 'Cancelled':
            return {
                'actual_time': None,
                'is_cancelled': True,
                'next_day': False
            }
            
        pattern = r'Dep (\d{2}:\d{2})(?:\s*\((\d{2}/\d{2}/\d{4})\))?'
        match = re.search(pattern, row['Status'])
        
        if not match:
            return {
                'actual_time': None,
                'is_cancelled': False,
                'next_day': False
            }
        
        actual_time = match.group(1)
        next_day = bool(match.group(2))
        
        return {
            'actual_time': actual_time,
            'is_cancelled': False,
            'next_day': next_day
        }
    
    status_info = df.apply(parse_status, axis=1)
    df['Actual_Time'] = status_info.apply(lambda x: x['actual_time'])
    df['Is_Cancelled'] = status_info.apply(lambda x: x['is_cancelled'])
    df['Next_Day'] = status_info.apply(lambda x: x['next_day'])
    
    # 3. Calculation of delays
    def calculate_delay(row):
        if row['Is_Cancelled'] or pd.isna(row['Actual_Time']):
            return None
            
        planned = datetime.strptime(row['Time'], '%H:%M')
        actual = datetime.strptime(row['Actual_Time'], '%H:%M')
        
        if row['Next_Day']:
            actual = actual + timedelta(days=1)
        elif actual.hour < 4 and planned.hour > 20:
            actual = actual + timedelta(days=1)
            
        delay = actual - planned
        delay_minutes = delay.total_seconds() / 60
        
        # 可以添加一个显式检查，确保提前起飞不会被视为延误
        return delay_minutes  # 允许返回负值表示提前起飞
    
    df['Delay_Minutes'] = df.apply(calculate_delay, axis=1)
    
    # 4. Mark delayed flights (delay > 30 minutes)
    df['Is_Delayed'] = (df['Delay_Minutes'] >= 30) & (~df['Is_Cancelled'])
    
    # 5. Select only necessary columns
    columns_to_keep = [
        'Date', 'Time', 'Airline', 'Actual_Time',
        'Is_Cancelled', 'Delay_Minutes', 'Is_Delayed'
    ]
    df = df[columns_to_keep]
    
    # 随后可以添加一个新列来标记提前起飞的航班
    df['Is_Early'] = df['Delay_Minutes'] < 0
    
    return df

def process_departure_files():
    """
    处理flight_data/depart目录下的所有出发航班数据文件
    返回: 包含所有处理后的出发航班数据的DataFrame
    """
    all_data = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    depart_folder = os.path.join(current_dir, "flight_data", "depart")
    
    # 获取depart文件夹下所有csv文件
    csv_files = [f for f in os.listdir(depart_folder) if f.endswith('.csv')]
    
    for file_name in csv_files:
        file_path = os.path.join(depart_folder, file_name)
        print(f"正在处理文件: {file_path}")
        
        # 读取CSV文件
        df = pd.read_csv(file_path)
        print(f"文件 {file_name} 的数据形状: {df.shape}")
        print(f"文件 {file_name} 的列名: {df.columns.tolist()}")
        
        # 重命名列名为大写
        df = df.rename(columns={
            'date': 'Date',
            'time': 'Time',
            'status': 'Status',
            'gate': 'Gate',
            'no': 'NO.'
        })
        
        # 预处理数据
        processed_df = preprocess_flight_data(df)
        all_data.append(processed_df)
        print(f"成功处理文件: {file_name}")
    
    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)
    return combined_df


if __name__ == "__main__":
    try:
        departure_flights_df = process_departure_files()
        print(f"出发航班数据量: {len(departure_flights_df)}")
        print("\n数据预览:")
        print(departure_flights_df.head())
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
          # 保存处理后的数据
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "flight_data", "processed_departure_flights.csv")
    departure_flights_df.to_csv(output_path, index=False)
    print(f"\n处理后的数据已保存至: {output_path}")

# # test
# test_data = {
#     'Date': ['2023/2/27', '2023/2/27','2023/2/27'],
#     'Time': ['23:50', '23:50','23:50'],
#     'Status': ['Dep 00:23 (28/02/2023)', 'Dep 00:00 (28/02/2023)','Dep 23:50'],
#     'Gate': ['2', '19','19'],
#     'NO.': ['CX 255', 'UO 624','UO 629']
# }


# test_df = pd.DataFrame(test_data)
# processed_df = preprocess_flight_data(test_df)
# print(processed_df)

