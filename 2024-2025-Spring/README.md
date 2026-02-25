# Cassandra and Spark Docker Setup

This repository contains a Docker Compose configuration for setting up a Cassandra database with Apache Spark integration.

## Prerequisites

Before you begin, you'll need to install Docker Engine and Docker Compose on your system. Follow the instructions below based on your operating system.

### Windows

#### Docker Desktop for Windows
1. Download Docker Desktop for Windows from the [official website](https://www.docker.com/products/docker-desktop)
2. Double-click the installer and follow the installation wizard
3. During installation, ensure that:
   - WSL 2 (Windows Subsystem for Linux) is enabled
   - Virtualization is enabled in your BIOS
4. After installation, restart your computer
5. Launch Docker Desktop from the Start menu
6. Wait for Docker to start (you'll see the Docker icon in your system tray)

### macOS

#### Docker Desktop for Mac
1. Download Docker Desktop for Mac from the [official website](https://www.docker.com/products/docker-desktop)
2. Double-click the downloaded `.dmg` file
3. Drag Docker.app to your Applications folder
4. Open Docker from your Applications folder
5. Follow the prompts to complete the installation
6. Wait for Docker to start (you'll see the Docker icon in your menu bar)

### Linux (Ubuntu/Debian)

#### Docker Engine
1. Update package index:
   ```bash
   sudo apt-get update
   ```
2. Install required packages:
   ```bash
   sudo apt-get install \
       ca-certificates \
       curl \
       gnupg \
       lsb-release
   ```
3. Add Docker's official GPG key:
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```
4. Set up the repository:
   ```bash
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
5. Install Docker Engine:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
   ```
6. Verify installation:
   ```bash
   sudo docker run hello-world
   ```

### Installing Docker Compose

#### Windows and macOS
Docker Compose is included with Docker Desktop installation.

#### Linux
1. Install Docker Compose using the package manager:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```
2. Verify installation:
   ```bash
   docker compose version
   ```

## Project Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Start the services:
   ```bash
   docker compose up -d
   ```

3. Verify the services are running:
   ```bash
   docker compose ps
   ```

## Services

The setup includes the following services:
- Cassandra (port 9042 for CQL, 9160 for Thrift)
- Spark Master (port 7077 for master, 8080 for web UI)
- Spark Worker (port 8081 for web UI)
- Spark Submit container for job submission

## Accessing Services

- Cassandra: `localhost:9042`
- Spark Master UI: `http://localhost:8080`
- Spark Worker UI: `http://localhost:8081`

## Stopping Services

To stop all services:
```bash
docker compose down
```

To stop and remove volumes:
```bash
docker compose down -v
```

## Troubleshooting

1. If you encounter permission issues on Linux, add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```
   Then log out and log back in for the changes to take effect.

2. If Docker Desktop fails to start on Windows:
   - Ensure virtualization is enabled in BIOS
   - Check if WSL 2 is properly installed
   - Run `wsl --update` in PowerShell as administrator

3. For macOS users:
   - If you see "Docker Desktop is starting..." for a long time, try resetting Docker Desktop from the menu bar icon
   - Ensure you have sufficient disk space and memory allocated to Docker Desktop 


## Cassandra Lab
1. Run the following command
    `docker exec -it cassandra cqlsh`
2. Create the keyspace
    `CREATE KEYSPACE IF NOT EXISTS sensor_data_ks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};`
3. Switch to the keyspace and create the table
    `USE sensor_data_ks;`
    and
    `CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp timestamp,
    temperature_C double,
    humidity_percent double,
    solar_irradiation_wm2 double,
    PRIMARY KEY (timestamp)
    );`
4. Please exit from the container and make sure that you are now on your PC in the power shell or other terminal, use command
    `exit` to exit the cassandra container!
5. Create virtual environment to generate the sensor data with anomalies
    - Create virtual env
    `virtualenv venv`
    - Install all the necessary packages
    `pip install -r requirements.txt`
    - Generate the randome data
    `python generate_data_with_anomalies.py --start "2020-01-01 00:00:00" --count 10000 --output data_with_anomalies.csv --anomaly_ratio 0.1`
6. Copy the generated CSV file, data_with_anomalies.csv to the cassandra container, with the following command
    `docker cp data_with_anomalies.csv cassandra:/data_with_anomalies.csv`
7. Make sure that you have exited the container and run the following command to push the data from the CSV file to the cassandra keyspace and the corresponding table, that we have created on step 3.
    `docker exec -it cassandra cqlsh -k sensor_data_ks -e "COPY sensor_readings (timestamp, temperature_C, humidity_percent, solar_irradiation_wm2) FROM '/data_with_anomalies.csv' WITH HEADER = TRUE;"`
8. Let's make sure that we have the data in the table
    - Attach to the container
        `docker exec -it cassandra cqlsh`
    - Switch to the sensor_data_ks database
        `USE sensor_data_ks;`
    - Run the query which will display top 10 entries in the table, where you just entered the data from the from CSV file
        `SELECT * FROM sensor_readings LIMIT 10;`
        as a result, you should see something like this
        ```
        timestamp                       | humidity_percent | solar_irradiation_wm2 | temperature_c
        ---------------------------------+------------------+-----------------------+---------------
        2020-04-06 11:00:00.000000+0000 |            62.64 |                375.08 |          23.1
        2020-02-16 22:30:00.000000+0000 |            72.51 |                275.52 |         18.55
        2020-02-17 12:00:00.000000+0000 |            58.29 |                687.35 |         22.16
        2020-01-24 07:15:00.000000+0000 |            45.39 |                724.99 |         21.91
        2020-02-18 17:45:00.000000+0000 |            52.16 |                181.06 |         24.15
        2020-02-22 03:30:00.000000+0000 |            61.14 |                338.49 |         24.04
        2020-04-03 15:30:00.000000+0000 |            70.35 |                688.37 |         22.96
        2020-04-03 10:15:00.000000+0000 |            64.58 |                356.62 |         23.63
        2020-02-16 00:00:00.000000+0000 |            41.19 |                474.16 |         27.49
        2020-01-13 06:15:00.000000+0000 |            74.35 |                398.17 |         22.59
        ```
9. Install once again the necessary packages using the command
    ```pip install -r requirements.txt```
    You can skip this step - it's just to make sure that you have all the necessary packages!
10. Run the plot generation script from cassandra with the following command and options
    ```python plot_cassandra_sensor_multi.py --keyspace sensor_data_ks --table sensor_readings --output multi_plot.png```