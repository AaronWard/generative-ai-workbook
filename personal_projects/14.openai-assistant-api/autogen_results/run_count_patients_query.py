# filename: run_count_patients_query.py
# Use the actual run_sql_tool function implementation to run this query

def run_sql_tool(sql_query):
    # The actual implementation should be here.
    pass

# SQL query to count the total number of patient records
sql_query = "SELECT COUNT(*) FROM patients;"

# Execute the query using the run_sql_tool function and output the result
result = run_sql_tool(sql_query)
print("Total number of patient records:", result)