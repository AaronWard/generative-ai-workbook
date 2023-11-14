# filename: calculate_mean_age.py
import sqlite3

# Connect to the SQLite database (You need to replace 'your_database.db' with the actual database file's path)
conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

# Execute SQL Query to find the mean age of patients diagnosed with COVID-19
try:
    cursor.execute("SELECT AVG(current_age) FROM patients WHERE diagnosed_covid = 1")
    mean_age = cursor.fetchone()[0]
    if mean_age is not None:
        print(f"The mean age of patients who have had COVID-19 is: {mean_age:.2f}")
    else:
        print("No patients with COVID-19 found or no age data available.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")

# Close the connection
conn.close()