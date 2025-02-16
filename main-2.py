import logging
import mysql.connector as sql
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

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

    # Drop table if it exists
    cursor.execute('DROP TABLE IF EXISTS model_evaluation')

    # Create new table for model evaluation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_evaluation (
            id INT AUTO_INCREMENT PRIMARY KEY,
            model_name VARCHAR(50),
            mse FLOAT,
            r2 FLOAT,
            mae FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    print("Table 'model_evaluation' is ready")

except sql.Error as e:
    logging.error(f"Database connection failed: {e}")
    raise

# Data collection for machine learning
query = "SELECT cpu_utilization, throughput, turnaround_time, waiting_time, response_time FROM performance"
cursor.execute(query)
data = cursor.fetchall()

# Convert the data into a DataFrame
columns = ['cpu_utilization', 'throughput', 'turnaround_time', 'waiting_time', 'response_time']
df = pd.DataFrame(data, columns=columns)

# Preprocessing: Handle missing values if any
df.fillna(df.mean(), inplace=True)

# Feature selection: Use relevant columns for the model
X = df[['cpu_utilization', 'throughput', 'turnaround_time', 'waiting_time']]  # Features
y = df['response_time']  # Target

# Scale features to standardize the dataset (important for some algorithms)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Initialize models
rf_model = RandomForestRegressor(random_state=42)
gb_model = GradientBoostingRegressor(random_state=42)

# Hyperparameter tuning using GridSearchCV for Random Forest
param_grid_rf = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20],
    'min_samples_split': [2, 5]
}
grid_search_rf = GridSearchCV(rf_model, param_grid_rf, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search_rf.fit(X_train, y_train)
rf_model_best = grid_search_rf.best_estimator_

# Hyperparameter tuning using GridSearchCV for Gradient Boosting
param_grid_gb = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1],
    'max_depth': [3, 5]
}
grid_search_gb = GridSearchCV(gb_model, param_grid_gb, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)
grid_search_gb.fit(X_train, y_train)
gb_model_best = grid_search_gb.best_estimator_

# Predictions with the best models
y_pred_rf = rf_model_best.predict(X_test)
y_pred_gb = gb_model_best.predict(X_test)

# Evaluate the models
rf_mse = mean_squared_error(y_test, y_pred_rf)
rf_r2 = r2_score(y_test, y_pred_rf)
rf_mae = mean_absolute_error(y_test, y_pred_rf)

gb_mse = mean_squared_error(y_test, y_pred_gb)
gb_r2 = r2_score(y_test, y_pred_gb)
gb_mae = mean_absolute_error(y_test, y_pred_gb)

# Log model evaluation results
logging.info(f"Random Forest MSE: {rf_mse}, R2: {rf_r2}, MAE: {rf_mae}")
logging.info(f"Gradient Boosting MSE: {gb_mse}, R2: {gb_r2}, MAE: {gb_mae}")

# Insert the results into the model_evaluation table
try:
    # Insert data for Random Forest model
    cursor.execute('''
        INSERT INTO model_evaluation (model_name, mse, r2, mae)
        VALUES (%s, %s, %s, %s)
    ''', ('Random Forest', rf_mse, rf_r2, rf_mae))

    # Insert data for Gradient Boosting model
    cursor.execute('''
        INSERT INTO model_evaluation (model_name, mse, r2, mae)
        VALUES (%s, %s, %s, %s)
    ''', ('Gradient Boosting', gb_mse, gb_r2, gb_mae))

    # Commit the changes to the database
    conn.commit()

    logging.info("Model evaluation data inserted into 'model_evaluation' table")

except sql.Error as e:
    logging.error(f"Failed to insert model evaluation data: {e}")
    conn.rollback()