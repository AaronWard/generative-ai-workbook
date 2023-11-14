# filename: run_sql_tool.py
import json

def run_sql_tool(sql_command):
    # This function should interface with an actual SQL tool to run the sql_command
    # and return the SQL query results in a list or single dictionary
    pass

# SQL command
sql_command = """
SELECT AVG(current_age) AS mean_age
FROM patients
WHERE diagnosed_covid = TRUE;
"""

# Execute the SQL command and get the result
result = run_sql_tool(sql_command)

# Check if we got any result and try to extract the mean age if possible
if result is not None:
    if isinstance(result, list) and len(result) > 0 and 'mean_age' in result[0]:
        # If the result is a list of dictionaries, extract the mean age from the first dictionary
        mean_age = result[0]['mean_age']
    elif isinstance(result, dict) and 'mean_age' in result:
        # If the result is a single dictionary, extract the mean age directly
        mean_age = result['mean_age']
    else:
        print("The result format is not recognized or 'mean_age' key is missing.")
    
    if 'mean_age' in locals():
        print(f"The mean age of patients who have had Covid is: {mean_age}")
else:
    print("The result is None. The SQL command did not return any data.")