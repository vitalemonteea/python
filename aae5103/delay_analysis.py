import pandas as pd
import os

# Get current file's absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Build complete path for CSV file
csv_path = os.path.join(current_dir, "flight_data", "processed_departure_flights.csv")

# Read processed data
df = pd.read_csv(csv_path)

# Convert date column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Filter date range and airlines
mask = (
    (df['Date'] >= '2023-06-01') & 
    (df['Date'] <= '2023-06-18') & 
    (df['Airline'].isin(['CX', 'UO', 'HX']))
)
filtered_df = df[mask]

# Calculate statistics by airline
results = filtered_df.groupby('Airline').agg({
    'Is_Delayed': ['count', 'sum'],  # count for total flights, sum for delayed flights
    'Delay_Minutes': 'mean'  # average delay time
}).round(2)

# Calculate delay rates
delay_rates = {}
for airline in results.index:
    delay_rates[airline] = (results.loc[airline, ('Is_Delayed', 'sum')] / 
                          results.loc[airline, ('Is_Delayed', 'count')] * 100).round(2)

# Format output results
print("Airline Delay Analysis (2023-06-01 to 2023-06-18)")
print("-" * 50)
for airline in ['CX', 'HX', 'UO']:
    if airline in results.index:
        total_flights = results.loc[airline, ('Is_Delayed', 'count')]
        delayed_flights = results.loc[airline, ('Is_Delayed', 'sum')]
        delay_rate = delay_rates[airline]
        avg_delay = results.loc[airline, ('Delay_Minutes', 'mean')]
        
        print(f"\n{airline} Airlines:")
        print(f"Total Flights: {total_flights}")
        print(f"Delayed Flights: {delayed_flights}")
        print(f"Delay Rate: {delay_rate}%")
        print(f"Average Delay Time: {avg_delay:.2f} minutes")