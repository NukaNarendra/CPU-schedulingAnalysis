# CPU Scheduling Analysis and System Error Detection

##  Project Overview
This project analyzes **CPU scheduling algorithms and system errors** by gathering real-time system metrics, training machine learning models, and visualizing performance through an interactive dashboard.

##  Objectives
1. **System Monitoring**: Collect CPU, memory, and disk usage metrics using `psutil`.
2. **Scheduling Analysis**: Evaluate FCFS, SJF, Round Robin, and Priority Scheduling.
3. **Error Detection**: Log system errors and deadlocks for better performance insights.
4. **Predictive Modeling**: Train ML models to forecast CPU utilization and response time.
5. **Visualization**: Display insights in an interactive dashboard using Dash and Plotly.

##  Project Structure

### **1. `main.py` (Data Collection & Preprocessing)**
- Uses `psutil` to **collect system metrics**.
- Stores data in **MySQL** (`cpu_scheduling` database).
- Implements **CPU scheduling algorithms** (FCFS, SJF, RR, Priority Scheduling).
- Logs **system events and errors**.

### **2. `main-2.py` (Machine Learning Model Training)**
- Fetches data from MySQL (`performance` table).
- Prepares dataset with **CPU utilization, turnaround time, waiting time, response time**.
- Trains **Random Forest & Gradient Boosting Regressor** models.
- Stores model evaluation metrics (MSE, R2, MAE) in MySQL (`model_evaluation` table).

### **3. `main-3.py` (Data Visualization Dashboard)**
- Fetches performance metrics from MySQL.
- Uses **Dash & Plotly** to create an interactive **CPU Scheduling Performance Dashboard**.
- Includes:
  - **CPU Utilization Over Time** (Line Chart)
  - **Comparison of Scheduling Metrics** (Bar Chart)

## 🛠 Setup & Installation

### **Required Installations**
Run the following command to install all dependencies:
```bash
pip install psutil mysql-connector-python pandas numpy scikit-learn dash plotly matplotlib seaborn
```

### **Breakdown by File**
1. **`main.py` (System Monitoring & Data Collection)**
   ```bash
   pip install psutil mysql-connector-python
   ```

2. **`main-2.py` (Machine Learning Model Training)**
   ```bash
   pip install pandas numpy scikit-learn mysql-connector-python
   ```

3. **`main-3.py` (Dashboard & Visualization)**
   ```bash
   pip install dash plotly pandas mysql-connector-python
   ```

### **Prerequisites**
- Python 3.8+
- MySQL Server
- Required Python libraries:
  ```bash
  pip install psutil mysql-connector-python pandas numpy scikit-learn dash plotly
  ```

### **Database Setup**
1. Create the MySQL database:
   ```sql
   CREATE DATABASE cpu_scheduling;
   ```
2. Run `main.py`, which **creates tables and collects system metrics**.

##  How to Run the Project

### **1. Run Data Collection (`main.py`)**
```bash
python main.py
```
- Gathers system metrics and stores them in MySQL.
- Runs CPU scheduling algorithms and logs performance.

### **2. Train Machine Learning Models (`main-2.py`)**
```bash
python main-2.py
```
- Fetches data from MySQL and trains models.
- Stores model evaluation metrics.

### **3. Start Dashboard (`main-3.py`)**
```bash
python main-3.py
```
- Launches the **interactive dashboard** on `http://127.0.0.1:8080/`.
- Select a scheduling algorithm to view insights.

##  Expected Deliverables
✔ Real-time system monitoring and error logging.  
✔ Performance evaluation of different CPU scheduling algorithms.  
✔ Machine learning models for predicting CPU utilization trends.  
✔ Interactive dashboard for visualizing scheduling performance.  

##  Future Enhancements
- **Integrate real-time alerts** for system errors & deadlocks.
- **Improve predictive models** with deep learning.
- **Enhance visualization** with more analytics & user controls.

---
###  Contributors
- Contributions are welcome! Feel free to open issues or submit pull requests to enhance the project.


