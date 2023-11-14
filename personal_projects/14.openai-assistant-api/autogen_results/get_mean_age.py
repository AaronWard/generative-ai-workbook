# filename: get_mean_age.py
import psycopg2

# Replace the following variables with your actual database connection details
db_name = "your_database_name"
db_user = "your_database_user"
db_password = "your_database_password"
db_host = "your_database_host"
db_port = "your_database_port"

# SQL query to get the mean age
query = """
SELECT AVG(current_age) AS mean_age
FROM patients
WHERE diagnosed_covid = true;
"""

try:
    # Connect to your database
    conn = psycopg2.connect(
        dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port
    )
    
    # Create a cursor object
    cur = conn.cursor()
    
    # Execute the query
    cur.execute(query)
    
    # Fetch the result
    mean_age = cur.fetchone()[0]
    print(f"The mean age of patients diagnosed with COVID-19 is: {mean_age}")
    
    # Close the cursor and connection to the database
    cur.close()
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")