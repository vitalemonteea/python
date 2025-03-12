import pandas as pd
import os
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "flight_data", "processed_departure_flights.csv")

df = pd.read_csv(csv_path)

# Convert Date to datetime and extract hour
df['Date'] = pd.to_datetime(df['Date'])
df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M').dt.hour

# Filter airlines and delayed flights
mask = (df['Airline'].isin(['CX', 'UO', 'HX'])) & (df['Is_Delayed'] == True)
delayed_flights = df[mask]

# Create figure with multiple subplots
plt.figure(figsize=(15, 10))

# 1. Bar Plot - Total delays by hour
plt.subplot(2, 1, 1)
total_hourly_delays = delayed_flights.groupby('Hour').size()
total_hourly_delays.plot(kind='bar')
plt.title('Total Hourly Distribution of Delayed Flights')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Delayed Flights')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# 2. Line Plot - Delays by airline
plt.subplot(2, 1, 2)
hourly_delays = delayed_flights.groupby(['Hour', 'Airline']).size().unstack(fill_value=0)
hourly_delays.plot(kind='line', marker='o')
plt.title('Hourly Distribution of Delayed Flights by Airline')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Delayed Flights')
plt.grid(True, alpha=0.3)
plt.legend(title='Airline')

# Adjust layout and save
plt.tight_layout()
output_path = os.path.join(current_dir, "flight_data", "delay_analysis_visualization.png")
plt.savefig(output_path, bbox_inches='tight', dpi=300)
plt.close()

# Print statistics
print("Hourly Delayed Flights Statistics by Airline")
print("-" * 50)
for airline in ['CX', 'HX', 'UO']:
    print(f"\n{airline} Airlines:")
    airline_delays = delayed_flights[delayed_flights['Airline'] == airline]
    hourly_stats = airline_delays.groupby('Hour').size()
    for hour in range(24):
        if hour in hourly_stats.index:
            print(f"Hour {hour:02d}:00 - {hour:02d}:59: {hourly_stats[hour]} delayed flights")
