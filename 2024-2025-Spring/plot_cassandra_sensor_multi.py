
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from cassandra.cluster import Cluster

def fetch_data_from_cassandra(keyspace, table, host='127.0.0.1', port=9042):
    cluster = Cluster([host], port=port)
    session = cluster.connect(keyspace)

    query = f"SELECT * FROM {table};"
    rows = session.execute(query)

    columns = rows.column_names
    data = {col: [] for col in columns}

    for row in rows:
        for col in columns:
            data[col].append(getattr(row, col))

    cluster.shutdown()
    return pd.DataFrame(data)

def plot_data(df, output_file):
    df = df.sort_values("timestamp")
    timestamp = df["timestamp"]
    sensor_columns = [col for col in df.columns if col != "timestamp"]

    num_plots = len(sensor_columns)
    fig, axs = plt.subplots(num_plots, 1, figsize=(12, 4 * num_plots), sharex=True)

    if num_plots == 1:
        axs = [axs]

    for i, col in enumerate(sensor_columns):
        axs[i].plot(timestamp, df[col], label=col)
        axs[i].set_ylabel(col)
        axs[i].legend(loc="upper right")

    axs[-1].set_xlabel("Timestamp")
    plt.suptitle("Sensor Data Time Series")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output_file)
    print(f"Multi-plot saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Read data from Cassandra and plot each column.")
    parser.add_argument("--keyspace", required=True, help="Cassandra keyspace name")
    parser.add_argument("--table", required=True, help="Cassandra table name")
    parser.add_argument("--host", default="127.0.0.1", help="Cassandra host address")
    parser.add_argument("--port", type=int, default=9042, help="Cassandra port")
    parser.add_argument("--output", default="sensor_multi_plot.png", help="Output plot image file")
    args = parser.parse_args()

    df = fetch_data_from_cassandra(args.keyspace, args.table, args.host, args.port)
    plot_data(df, args.output)

if __name__ == "__main__":
    main()
