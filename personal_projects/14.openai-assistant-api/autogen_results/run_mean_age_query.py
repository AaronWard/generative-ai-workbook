# filename: run_mean_age_query.py

# Placeholder for the actual run_sql_tool function implementation.
# Please ensure that this function is defined correctly according to your provided tools and environment.

def run_sql_tool(sql_query):
    # The actual implementation should be here.
    # This function should execute the passed SQL query and return the result.
    pass

# SQL query to select the mean age of patients who have been diagnosed with COVID-19
sql_query = """
SELECT AVG(age_at_diagnosis) AS mean_age_at_diagnosis
FROM patients
WHERE diagnosed_covid = True;
"""

# Execute the query using the run_sql_tool function and store the result
result = run_sql_tool(sql_query)

# Output the result to the user
print(result)