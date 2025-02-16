import psutil
import time
import mysql.connector as sql
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection setup
try:
    conn = sql.connect(
        host="localhost",
        port="3306",
        user="root",
        password="",#your password
        database="cpu_scheduling",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    print('Database connection established')

    # Drop tables if they exist
    cursor.execute('DROP TABLE IF EXISTS system_metrics')
    cursor.execute('DROP TABLE IF EXISTS performance')
    cursor.execute('DROP TABLE IF EXISTS system_events')

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_percent FLOAT,
            cpu_count INT,
            memory_free FLOAT,
            memory_used FLOAT,
            disk_used FLOAT,
            bytes_received BIGINT,
            bytes_sent BIGINT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_utilization FLOAT,
            throughput INT,
            turnaround_time FLOAT,
            waiting_time FLOAT,
            response_time FLOAT,
            algorithm VARCHAR(50)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type VARCHAR(50),
            event_description TEXT
        );
    ''')
    conn.commit()
    print("Tables 'system_metrics', 'performance', and 'system_events' are ready")

except sql.Error as e:
    logging.error(f"Database connection failed: {e}")
    raise


# Log system event
def log_system_event(event_type, description):
    try:
        insert_event_query = '''
            INSERT INTO system_events (event_type, event_description)
            VALUES (%s, %s)
        '''
        cursor.execute(insert_event_query, (event_type, description))
        conn.commit()
        logging.info(f"Logged system event: {event_type} - {description}")
    except sql.Error as e:
        logging.error(f"Failed to log system event: {e}")
        conn.rollback()


# Function to collect system metrics
def collect_system_metrics():
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)
    memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    system_metrics = {
        'cpu_percent': cpu_percent,
        'cpu_count': cpu_count,
        'memory_free': memory.available / (1024 ** 2),  # Convert bytes to MB
        'memory_used': memory.used / (1024 ** 2),  # Convert bytes to MB
        'disk_used': disk_usage.percent,
        'bytes_received': net_io.bytes_recv,
        'bytes_sent': net_io.bytes_sent
    }

    return system_metrics


# Function to insert system metrics into the database
def insert_system_metrics(system_metrics):
    try:
        insert_query = '''
            INSERT INTO system_metrics (cpu_percent, cpu_count, memory_free, memory_used, disk_used, bytes_received, bytes_sent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (
            system_metrics['cpu_percent'],
            system_metrics['cpu_count'],
            system_metrics['memory_free'],
            system_metrics['memory_used'],
            system_metrics['disk_used'],
            system_metrics['bytes_received'],
            system_metrics['bytes_sent']
        ))
        conn.commit()
        logging.info("System metrics inserted successfully")
    except sql.Error as e:
        logging.error(f"Error inserting system metrics: {e}")
        conn.rollback()


# Function to collect process data
def collect_process_data():
    processes = []

    for p in psutil.process_iter(['pid', 'cpu_times', 'create_time', 'memory_info', 'name']):
        try:
            pid = p.info["pid"]
            arrival_time = p.info["create_time"]  # Arrival time of process
            burst_time = p.cpu_times().user + p.cpu_times().system  # Total CPU time used
            memory_usage = p.memory_info().rss / (1024 * 1024)  # Convert to MB
            priority = p.nice()  # Process priority

            # Simulate real-time wait_time and turnaround_time
            wait_time = max(0, int(time.time() - arrival_time))  # Simulated wait time
            turnaround_time = wait_time + burst_time  # Turnaround time

            process_data = {
                "pid": pid,
                "arrival_time": arrival_time,
                "burst_time": burst_time,
                "memory_usage": memory_usage,
                "priority": priority,
                "wait_time": wait_time,
                "turnaround_time": turnaround_time,
                "name": p.info["name"]  # Process name
            }
            processes.append(process_data)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes


def fcfs(processes):
    total_wait_time = 0
    total_turnaround_time = 0
    processes = sorted(processes, key=lambda p: p['arrival_time'])

    for i, process in enumerate(processes):
        wait_time = sum(p['burst_time'] for p in processes[:i])
        total_wait_time += wait_time
        total_turnaround_time += wait_time + process['burst_time']

    avg_wait_time = total_wait_time / len(processes)
    avg_turnaround_time = total_turnaround_time / len(processes)
    return avg_wait_time, avg_turnaround_time


def sjf(processes):
    processes = sorted(processes, key=lambda p: p['burst_time'])
    return fcfs(processes)


def round_robin(processes, time_slice=2):
    n = len(processes)
    remaining_burst_times = [p['burst_time'] for p in processes]
    wait_times = [0] * n
    t = 0  # Current time in the simulation

    while True:
        done = True
        for i in range(n):
            if remaining_burst_times[i] > 0:
                done = False
                if remaining_burst_times[i] > time_slice:
                    t += time_slice
                    remaining_burst_times[i] -= time_slice
                else:
                    t += remaining_burst_times[i]
                    wait_times[i] = t - processes[i]['burst_time']
                    remaining_burst_times[i] = 0

        if done:
            break

    avg_wait_time = sum(wait_times) / n
    avg_turnaround_time = sum(p['turnaround_time'] for p in processes) / n
    return avg_wait_time, avg_turnaround_time


def priority_scheduling(processes):
    processes = sorted(processes, key=lambda p: p['priority'])
    return fcfs(processes)


# Function to monitor and store system metrics
def monitor_system_metrics(iterations=100):
    try:
        for p7 in range(iterations):
            # Collect and insert system metrics (CPU, memory, disk usage)
            system_metrics = collect_system_metrics()  # Function to collect system-level metrics
            insert_system_metrics(system_metrics)  # Insert system metrics into the database

            # Collect process-level data for CPU scheduling algorithms
            processes = collect_process_data()

            # Gather performance data for each algorithm
            algorithms = ["FCFS", "SJF", "RR", "Priority"]
            for algorithm in algorithms:
                if algorithm == "FCFS":
                    avg_wait_time, avg_turnaround_time = fcfs(processes)
                elif algorithm == "SJF":
                    avg_wait_time, avg_turnaround_time = sjf(processes)
                elif algorithm == "RR":
                    avg_wait_time, avg_turnaround_time = round_robin(processes)
                elif algorithm == "Priority":
                    avg_wait_time, avg_turnaround_time = priority_scheduling(processes)

                # Insert performance metrics into the database
                cpu_utilization = system_metrics['cpu_percent']
                throughput = len(processes)  # Assuming throughput as number of processes (can be refined)
                response_time = avg_wait_time  # Assuming response time is equivalent to waiting time for simplicity

                insert_query = '''
                    INSERT INTO performance (timestamp, cpu_utilization, throughput, turnaround_time, 
                                            waiting_time, response_time, algorithm)
                    VALUES (NOW(), %s, %s, %s, %s, %s, %s)
                '''
                cursor.execute(insert_query, (
                    cpu_utilization, throughput, avg_turnaround_time, avg_wait_time, response_time, algorithm
                ))
                conn.commit()

            logging.info("Performance metrics inserted for all algorithms")

    except sql.Error as e:
        error_message = f"Error while inserting metrics into database: {e}"
        logging.error(error_message)
        log_system_event("Database Error", error_message)
        conn.rollback()

    except Exception as e:
        error_message = f"Unexpected error: {e}"
        logging.error(error_message)
        log_system_event("System Error", error_message)

    # Pause before next iteration
    time.sleep(1)

# Start monitoring in a separate thread to avoid blocking the main thread
monitor_thread = threading.Thread(target=monitor_system_metrics)
monitor_thread.start()