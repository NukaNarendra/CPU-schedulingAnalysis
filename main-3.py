import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import mysql.connector as sql
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
try:
    conn = sql.connect(
        host="localhost",
        port="3306",
        user="root",
        password="",#your_password
        database="cpu_scheduling",
        auth_plugin='mysql_native_password'
    )
    cursor = conn.cursor()
    logging.info("Database connection established")
except sql.Error as e:
    logging.error(f"Database connection failed: {e}")
    raise

# Fetch data from the 'performance' table
def fetch_performance_data():
    try:
        query = "SELECT timestamp, cpu_utilization, throughput, turnaround_time, waiting_time, response_time, algorithm FROM performance"
        cursor.execute(query)
        data = cursor.fetchall()
        columns = ['timestamp', 'cpu_utilization', 'throughput', 'turnaround_time', 'waiting_time', 'response_time', 'algorithm']
        df = pd.DataFrame(data, columns=columns)
        logging.info("Performance data fetched successfully")
        return df
    except sql.Error as e:
        logging.error(f"Error fetching performance data: {e}")
        return pd.DataFrame()

# Initialize the Dash app
app = dash.Dash(__name__)

# Fetch data for visualization
data = fetch_performance_data()

# App layout
app.layout = html.Div([
    html.H1("CPU Scheduling Performance Dashboard", style={'text-align': 'center'}),

    # Dropdown to select algorithm
    html.Div([
        html.Label("Select Scheduling Algorithm:"),
        dcc.Dropdown(
            id='algorithm-dropdown',
            options=[{'label': algo, 'value': algo} for algo in data['algorithm'].unique()],
            value=data['algorithm'].unique()[0],  # Default value
            clearable=False
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    # Visualization: CPU Utilization Over Time
    dcc.Graph(id='cpu-utilization-graph'),

    # Visualization: Comparison of Metrics
    dcc.Graph(id='metrics-comparison-graph')
])

# Callback to update graphs based on the selected algorithm
@app.callback(
    [
        Output('cpu-utilization-graph', 'figure'),
        Output('metrics-comparison-graph', 'figure')
    ],
    [Input('algorithm-dropdown', 'value')]
)
def update_graphs(selected_algorithm):
    filtered_data = data[data['algorithm'] == selected_algorithm]

    # CPU Utilization Over Time
    cpu_utilization_fig = px.line(
        filtered_data,
        x='timestamp',
        y='cpu_utilization',
        title=f"CPU Utilization Over Time ({selected_algorithm})",
        labels={'cpu_utilization': 'CPU Utilization (%)', 'timestamp': 'Timestamp'},
        markers=True
    )

    # Comparison of Metrics
    metrics_comparison_fig = px.bar(
        filtered_data,
        x='timestamp',
        y=['throughput', 'turnaround_time', 'waiting_time', 'response_time'],
        title=f"Metrics Comparison ({selected_algorithm})",
        labels={'value': 'Metric Value', 'timestamp': 'Timestamp'},
        barmode='group'
    )

    return cpu_utilization_fig, metrics_comparison_fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True,port=8080)