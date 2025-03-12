import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "flight_data", "processed_departure_flights.csv")

df = pd.read_csv(csv_path)

df['Date'] = pd.to_datetime(df['Date'])

# Filter date range and airlines
mask = (
    (df['Date'] >= '2023-06-01') & 
    (df['Date'] <= '2023-06-18') & 
    (df['Airline'].isin(['CX', 'UO', 'HX']))
)
filtered_df = df[mask]

# 计算每个航空公司的总航班和延误航班
airline_stats = {}
for airline in ['CX', 'HX', 'UO']:
    airline_data = filtered_df[filtered_df['Airline'] == airline]
    total_flights = len(airline_data)
    delayed_flights = sum(airline_data['Is_Delayed'])
    
    # 只计算延误航班的平均延误时间
    delayed_only = airline_data[airline_data['Is_Delayed'] == True]
    avg_delay = delayed_only['Delay_Minutes'].mean() if len(delayed_only) > 0 else 0
    
    airline_stats[airline] = {
        'total_flights': total_flights,
        'delayed_flights': delayed_flights,
        'delay_rate': (delayed_flights / total_flights * 100) if total_flights > 0 else 0,
        'avg_delay': avg_delay
    }

# 打印结果
print("Airline Delay Analysis (2023-06-01 to 2023-06-18)")
print("-" * 50)
for airline, stats in airline_stats.items():
    print(f"\n{airline} Airlines:")
    print(f"Total Flights: {stats['total_flights']}")
    print(f"Delayed Flights: {stats['delayed_flights']}")
    print(f"Delay Rate: {stats['delay_rate']:.2f}%")
    print(f"Average Delay Time: {stats['avg_delay']:.2f} minutes")