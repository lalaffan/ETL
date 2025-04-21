import os
import pandas as pd
import psycopg2
from pandasql import sqldf
from pytz import timezone

dsn = os.getenv('DSN')

try:
    cnn = psycopg2.connect(dsn)
    cur = cnn.cursor()

    query = '''
    SELECT period, respondent, respondent_name, fueltype, type_name, value
    FROM "hourly_generation_by_energy_source_raw";
    '''
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    df = pd.DataFrame(rows, columns=colnames)

    cur.close()
    cnn.close()

except Exception as e:
    print(f"An error occurred: {e}")


query_mapping = '''
SELECT "BA_Code", "BA_Name", region_code, region_name
FROM "BA_region_mapping";
'''

cnn = psycopg2.connect(dsn)
cur = cnn.cursor()
cur.execute(query_mapping)

rows = cur.fetchall()
colnames = [desc[0] for desc in cur.description]

df_mapping = pd.DataFrame(rows, columns=colnames)

# Merge hourly_energy_generation with BA_region mapping on BA
result_inner = pd.merge(df, df_mapping, left_on='respondent', right_on='BA_Code', how='inner')

# convet utc to eastern
result_inner['period'] = pd.to_datetime(result_inner['period'])
result_inner['period'] = result_inner['period'].dt.tz_localize('UTC')
result_inner['period'] = result_inner['period'].dt.tz_convert('US/Eastern')
result_inner['period'] = result_inner['period'].dt.tz_localize(None)


query_hs = '''
SELECT *, DATE(period) AS date, strftime('%H', period) AS hour_start
FROM result_inner;
'''
query_hs_df = sqldf(query_hs)


query_hour_end = '''
SELECT *,CASE
WHEN (CAST(hour_start AS INTEGER)) % 24 = 0 THEN DATE(datetime(date, '-1 day')) 
ELSE date END AS date_new,
printf('%02d', (CASE WHEN (CAST(hour_start AS INTEGER)) % 24 = 0 THEN 24 ELSE (CAST(hour_start AS INTEGER)) % 24 END)) AS hour_end
FROM query_hs_df;
'''
query_hour_end_df = sqldf(query_hour_end)


query_final = '''
SELECT respondent_name as balancing_authority,respondent as balancing_authority_code,type_name as energy_source,fueltype as energy_source_code,
value,region_name,region_code,date_new,hour_end
FROM query_hour_end_df;
'''
final_df = sqldf(query_final)


pivot_query = '''
SELECT balancing_authority,balancing_authority_code,energy_source,energy_source_code,
region_name,region_code,date_new,
       SUM(CASE WHEN hour_end = '01' THEN value ELSE 0 END) AS hour_ending_01,
       SUM(CASE WHEN hour_end = '02' THEN value ELSE 0 END) AS hour_ending_02,
       SUM(CASE WHEN hour_end = '03' THEN value ELSE 0 END) AS hour_ending_03,
       SUM(CASE WHEN hour_end = '04' THEN value ELSE 0 END) AS hour_ending_04,
       SUM(CASE WHEN hour_end = '05' THEN value ELSE 0 END) AS hour_ending_05,
       SUM(CASE WHEN hour_end = '06' THEN value ELSE 0 END) AS hour_ending_06,
       SUM(CASE WHEN hour_end = '07' THEN value ELSE 0 END) AS hour_ending_07,
       SUM(CASE WHEN hour_end = '08' THEN value ELSE 0 END) AS hour_ending_08,
       SUM(CASE WHEN hour_end = '09' THEN value ELSE 0 END) AS hour_ending_09,
       SUM(CASE WHEN hour_end = '10' THEN value ELSE 0 END) AS hour_ending_10,
       SUM(CASE WHEN hour_end = '11' THEN value ELSE 0 END) AS hour_ending_11,
       SUM(CASE WHEN hour_end = '12' THEN value ELSE 0 END) AS hour_ending_12,
       SUM(CASE WHEN hour_end = '13' THEN value ELSE 0 END) AS hour_ending_13,
       SUM(CASE WHEN hour_end = '14' THEN value ELSE 0 END) AS hour_ending_14,
       SUM(CASE WHEN hour_end = '15' THEN value ELSE 0 END) AS hour_ending_15,
       SUM(CASE WHEN hour_end = '16' THEN value ELSE 0 END) AS hour_ending_16,
       SUM(CASE WHEN hour_end = '17' THEN value ELSE 0 END) AS hour_ending_17,
       SUM(CASE WHEN hour_end = '18' THEN value ELSE 0 END) AS hour_ending_18,
       SUM(CASE WHEN hour_end = '19' THEN value ELSE 0 END) AS hour_ending_19,
       SUM(CASE WHEN hour_end = '20' THEN value ELSE 0 END) AS hour_ending_20,
       SUM(CASE WHEN hour_end = '21' THEN value ELSE 0 END) AS hour_ending_21,
       SUM(CASE WHEN hour_end = '22' THEN value ELSE 0 END) AS hour_ending_22,
       SUM(CASE WHEN hour_end = '23' THEN value ELSE 0 END) AS hour_ending_23,
       SUM(CASE WHEN hour_end = '24' THEN value ELSE 0 END) AS hour_ending_24
FROM final_df
GROUP BY balancing_authority, date_new;
'''

pivot_df = sqldf(pivot_query)

# Daily column calculation
hour_cols = [col for col in pivot_df.columns if col.startswith('hour')]
pivot_df['daily'] = pivot_df[hour_cols].sum(axis=1)

pivot_df['region_code'] = pivot_df['region_code'].replace('MIDW', 'MW')
pivot_df = pivot_df.rename(columns={'date_new': 'date'})

print(pivot_df.iloc[1:5][['balancing_authority', 'balancing_authority_code', 'energy_source', 'energy_source_code', 'region_name', 'region_code', 'date', 'daily']])

# Final target table
merge_query = '''
SELECT region_name,region_code,strftime('%Y-%m', date) AS measurement_date,
SUM(daily) AS monthly_energy_generation
FROM pivot_df
GROUP BY region_name, region_code, strftime('%Y-%m', date);
'''

merge_query_df = sqldf(merge_query)

print(merge_query_df.iloc[1:])
