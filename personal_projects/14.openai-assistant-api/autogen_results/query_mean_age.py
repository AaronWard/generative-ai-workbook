# filename: query_mean_age.py

import psycopg2

# Please replace the following variables with your database connection details
dbname = "your_database_name"
user = "your_db_username"
password = "your_db_password"
host = "your_db_host"
port = "your_db_port"

# Establish a connection to the database
try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    # SQL query to find the mean age of patients diagnosed with COVID
    query = "SELECT AVG(current_age) AS mean_age FROM patients WHERE diagnosed_covid = true;"

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()
    mean_age = result[0] if result else None

    # Output the result
    print(f"The mean age of patients who have had COVID-19 is: {mean_age}")

except psycopg2.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()