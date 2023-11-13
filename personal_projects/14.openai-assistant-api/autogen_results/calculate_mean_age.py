# filename: calculate_mean_age.py

import psycopg2

# TODO: Replace the following placeholders with your actual database connection information
db_name = 'your_database_name'  # Replace with your actual database name
db_user = 'your_database_user'  # Replace with your actual database user
db_pass = 'your_database_password'  # Replace with your actual database password
db_host = 'your_database_host'  # Replace with your actual database host

# Connect to your database
conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host)

# Create a cursor object
cur = conn.cursor()

# Execute the SQL query
cur.execute("SELECT AVG(current_age) as mean_age FROM patients WHERE diagnosed_covid = true;")

# Fetch the result
mean_age = cur.fetchone()[0]

# Close the cursor and connection
cur.close()
conn.close()

# Check if mean_age is None (which would happen if no patients with diagnosed_covid exist)
if mean_age is None:
    print("No patients with diagnosed COVID-19 were found in the database.")
else:
    # Print the mean age
    print(f"The mean age of patients who have had COVID-19 is: {mean_age}")