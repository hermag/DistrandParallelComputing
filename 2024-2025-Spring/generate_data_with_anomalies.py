import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import random

def generate_sensor_data(start_date, num_entries, interval_minutes=15, anomaly_ratio=0.05):
    start_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    timestamps = [start_time + timedelta(minutes=i * interval_minutes) for i in range(num_entries)]

    temperature = np.random.normal(loc=22, scale=3, size=num_entries)
    humidity = np.random.normal(loc=60, scale=10, size=num_entries)
    solar_irradiation = np.random.normal(loc=400, scale=150, size=num_entries)

    # Introduce anomalies
    num_anomalies = int(num_entries * anomaly_ratio)
    anomaly_indices = random.sample(range(num_entries), num_anomalies)

    for idx in anomaly_indices:
        temperature[idx] = random.choice([np.random.uniform(-10, 5), np.random.uniform(40, 60)])
        humidity[idx] = random.choice([np.random.uniform(0, 10), np.random.uniform(90, 100)])
        solar_irradiation[idx] = random.choice([0, np.random.uniform(1200, 1600)])

    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_C": np.round(temperature, 2),
        "humidity_%": np.round(humidity, 2),
        "solar_irradiation_W/m2": np.clip(np.round(solar_irradiation, 2), 0, None)
    })

    return df

def main():
    parser = argparse.ArgumentParser(description="Generate sensor data CSV with anomalies.")
    parser.add_argument("--start", required=True, help="Start date in format YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--count", type=int, required=True, help="Number of data entries")
    parser.add_argument("--output", default="sensor_data.csv", help="Output CSV file name")
    parser.add_argument("--anomaly_ratio", type=float, default=0.05, help="Ratio of anomalies (e.g., 0.05 for 5%)")
    args = parser.parse_args()

    df = generate_sensor_data(args.start, args.count, anomaly_ratio=args.anomaly_ratio)
    df.to_csv(args.output, index=False)
    print(f"Generated {args.count} entries with {int(args.count * args.anomaly_ratio)} anomalies -> Saved to {args.output}")

if __name__ == "__main__":
    main()
