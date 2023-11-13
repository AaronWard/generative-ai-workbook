SELECT AVG(current_age) AS mean_age
FROM patients
WHERE diagnosed_covid = TRUE;