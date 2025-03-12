import pandas as pd
import os

# 读取处理后的数据
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "flight_data", "processed_departure_flights.csv")

df = pd.read_csv(csv_path)

# 筛选HX航空公司的数据
hx_data = df[df['Airline'] == 'HX']

# 筛选日期范围
hx_data['Date'] = pd.to_datetime(hx_data['Date'])
hx_data = hx_data[(hx_data['Date'] >= '2023-06-01') & (hx_data['Date'] <= '2023-06-18')]

# 筛选延误航班
hx_delayed = hx_data[hx_data['Delay_Minutes'] >= 30]

# 打印统计信息
total_flights = len(hx_data)
delayed_flights = len(hx_delayed)
delay_rate = (delayed_flights / total_flights * 100) if total_flights > 0 else 0
avg_delay = hx_delayed['Delay_Minutes'].mean() if delayed_flights > 0 else 0

print(f"HX Airlines Delay Analysis (2023-06-01 to 2023-06-18)")
print(f"Total Flights: {total_flights}")
print(f"Delayed Flights: {delayed_flights}")
print(f"Delay Rate: {delay_rate:.2f}%")
print(f"Average Delay Time: {avg_delay:.2f} minutes")
print("\nDelayed Flight Details:")
print("-" * 80)

# 打印延误航班详情
columns_to_display = ['Date', 'Time', 'Actual_Time', 'Delay_Minutes', 'Is_Delayed']
print(hx_delayed[columns_to_display].sort_values('Delay_Minutes', ascending=False).to_string())

# 统计延误时长分布
print("\nDelay Duration Distribution:")
delay_bins = [30, 60, 90, 120, float('inf')]
delay_labels = ['30-60 min', '60-90 min', '90-120 min', '120+ min']
hx_delayed['Delay_Category'] = pd.cut(hx_delayed['Delay_Minutes'], bins=delay_bins, labels=delay_labels)
delay_distribution = hx_delayed['Delay_Category'].value_counts().sort_index()
for category, count in delay_distribution.items():
    print(f"{category}: {count} flights ({count/delayed_flights*100:.1f}%)") 