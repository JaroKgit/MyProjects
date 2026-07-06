-- Data Engineer Internship Task – Livesport
-- Author: Jaroslav Krejčí

-- 1) STEP - Load datasets into DuckDB tables
-- Two versions of player data are loaded from CSV files
-- Two tables have been created from separate datasets

CREATE TABLE players_v1 AS 
SELECT * FROM read_csv_auto('players_data_v1.csv');
CREATE TABLE players_v2 AS 
SELECT * FROM read_csv_auto('players_data_v2.csv'); -- creates tables

-- 2) STEP - Find the differences between tables
-- Using SQL prompts determine how and where are tables different
-- 2)1) Does the row count differ

SELECT COUNT(*) FROM players_v1
SELECT COUNT(*) FROM players_v2  -- counts how many rows there is in each table

[(197516,)]
[(205070,)]

-- In the second table is 7554 more rows
-- The difference suggest that second dataset will not be precise copy of the first table.
-- The difference is likely caused by: duplicated records, newly added users
-- At this stage, the cause cannot be confirmed without further analysis

-- 2)2) Are in tables some missing values?
-- Firstly I will look into NULL values and '' values where it makes sense

SELECT 
    'players_v1' AS table_name,

    COUNT(*) FILTER (WHERE as_of IS NULL) AS missing_as_of,
    COUNT(*) FILTER (WHERE country IS NULL) AS missing_country,
    COUNT(*) FILTER (WHERE tracker_id IS NULL) AS missing_tracker_id,
    COUNT(*) FILTER (WHERE tracker_name IS NULL) AS missing_tracker_name,
    COUNT(*) FILTER (WHERE user_id IS NULL) AS missing_user_id,
    COUNT(*) FILTER (WHERE signup_date IS NULL) AS missing_signup_date,
    COUNT(*) FILTER (WHERE signup_year IS NULL) AS missing_signup_year,
    COUNT(*) FILTER (WHERE first_deposit_date IS NULL) AS missing_first_deposit_date,
    COUNT(*) FILTER (WHERE first_deposit_year IS NULL) AS missing_first_deposit_year,
    COUNT(*) FILTER (WHERE first_deposit_amount IS NULL) AS missing_first_deposit_amount,
    COUNT(*) FILTER (WHERE sports_bets_turnover IS NULL) AS missing_sports_bets_turnover,
    COUNT(*) FILTER (WHERE sportsbook_net_revenue IS NULL) AS missing_sportsbook_net_revenue,
    COUNT(*) FILTER (WHERE total_net_revenue IS NULL) AS missing_total_net_revenue,
    COUNT(*) FILTER (WHERE deposits IS NULL) AS missing_deposits,
    COUNT(*) FILTER (WHERE revenue IS NULL) AS missing_revenue,
    COUNT(*) FILTER (WHERE project_name IS NULL) AS missing_project_name,
    COUNT(*) FILTER (WHERE platform IS NULL) AS missing_platform

FROM players_v1

UNION ALL

SELECT 
    'players_v2',

    COUNT(*) FILTER (WHERE as_of IS NULL),
    COUNT(*) FILTER (WHERE country IS NULL),
    COUNT(*) FILTER (WHERE tracker_id IS NULL),
    COUNT(*) FILTER (WHERE tracker_name IS NULL),
    COUNT(*) FILTER (WHERE user_id IS NULL),
    COUNT(*) FILTER (WHERE signup_date IS NULL),
    COUNT(*) FILTER (WHERE signup_year IS NULL),
    COUNT(*) FILTER (WHERE first_deposit_date IS NULL),
    COUNT(*) FILTER (WHERE first_deposit_year IS NULL),
    COUNT(*) FILTER (WHERE first_deposit_amount IS NULL),
    COUNT(*) FILTER (WHERE sports_bets_turnover IS NULL),
    COUNT(*) FILTER (WHERE sportsbook_net_revenue IS NULL),
    COUNT(*) FILTER (WHERE total_net_revenue IS NULL),
    COUNT(*) FILTER (WHERE deposits IS NULL),
    COUNT(*) FILTER (WHERE revenue IS NULL),
    COUNT(*) FILTER (WHERE project_name IS NULL),
    COUNT(*) FILTER (WHERE platform IS NULL)

FROM players_v2; -- counts null and missing values in each dataset

[('players_v1', 0, 0, 0, 12265, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), 
('players_v2', 0, 0, 982, 11760, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]

-- NULL values are mostly in 4th row - tracker_name and 3rd row - tracker_id
-- This suggest minor tracking problem or pairing problem
-- On the other hand each transaction is paired correctly since no user_id is missing
-- During double checking in .xls I encountered 7 missing values in players_v1, row 3rd
-- Unfortunatelly I weren't able to adress this incontinuity

-- Further I check whether there are unaccounted countries or signup_years in each document
-- It makes sense only for country, platform, project_name, 
-- Revenue, deposits, signup_date - it is expacteble that they will differ, same with trackers and user_id

SELECT DISTINCT country
FROM players_v1
EXCEPT
SELECT DISTINCT country  -- compares whether there are more countries in v1 in comparison with v2
FROM players_v2;

SELECT DISTINCT country
FROM players_v2
EXCEPT
SELECT DISTINCT country  -- compares whether there are more countries in v2 in comparison with v1
FROM players_v1;

[('New Zealand',), ('Canada - Ontario',)]
[]

SELECT DISTINCT platform
FROM players_v1
EXCEPT
SELECT DISTINCT platform  -- compares whether there are more platforms in v1 in comparison with v2
FROM players_v2;

SELECT DISTINCT platform
FROM players_v2
EXCEPT
SELECT DISTINCT platform -- compares whether there are more platforms in v2 in comparison with v1
FROM players_v1;

[('Huawei',)]
[]

SELECT DISTINCT signup_year
FROM players_v1
EXCEPT
SELECT DISTINCT signup_year  -- compares whether there are more signup years in v1 in comparison with v2
FROM players_v2;

SELECT DISTINCT signup_year
FROM players_v2
EXCEPT
SELECT DISTINCT signup_year -- compares whether there are more signup years in v2 in comparison with v1
FROM players_v1;

[(2009,), (2025,), (2022,), (2013,), (2017,), (2024,), (2008,), (2023,), (2019,), (2012,), (2020,), (2011,), (2014,), (2010,), (2026,), (2018,), (2016,), (2015,), (2021,)]
[(9999,)]

SELECT DISTINCT project_name
FROM players_v1
EXCEPT
SELECT DISTINCT project_name  -- compares whether there are more project_names in v1 in comparison with v2
FROM players_v2;

SELECT DISTINCT project_name
FROM players_v2
EXCEPT
SELECT DISTINCT project_name -- compares whether there are more project_names in v2 in comparison with v1
FROM players_v1;

[]
[]

-- Country: In the second table are missing countries Canada-Ontario and New Zealand
--          This suggest that may have been misplaced or information in second dataset are from different part of the world
-- Platform: In the second table is not "Huawei", this suggest that there may not have been users with Huawei or it is under "android"
-- Signup_year: There arouse problem, since data in second table have faulty signup_year (all of them have 9999)
--              this suggest that there is problem with correct extraction of the year from signup_date
-- Project_name: No distinction

-- 2)3) Are in each table duplicated records?
-- I am looking for 1:1 copies of groups 

SELECT COUNT(*) AS duplicate_groups
FROM (
    SELECT *
    FROM players_v1
    GROUP BY ALL
    HAVING COUNT(*) > 1  -- looks for 1:1 duplicate groups in tables
);

SELECT COUNT(*) AS duplicate_groups2
FROM (
    SELECT *
    FROM players_v2
    GROUP BY ALL
    HAVING COUNT(*) > 1
);

[(39,)]
[(8835,)]

-- In the first table are 39 duplicities
-- More rows in second table are explained, because it has almost 9000 duplicities
-- Further I will look into how many rows are only in 1st table and how many are unique in the 2nd table

SELECT COUNT(*) AS only_in_v2
FROM players_v2 v2
LEFT JOIN players_v1 v1
  ON v2.user_id = v1.user_id
 AND v2.as_of = v1.as_of
WHERE v1.user_id IS NULL; -- This code looks for rows that are in v2 but are not in v1 based on same user_id and as_of

[(0),]

SELECT COUNT(*) AS only_in_v1
FROM players_v1 v1
LEFT JOIN players_v2 v2
  ON v1.user_id = v2.user_id
 AND v1.as_of = v2.as_of
WHERE v2.user_id IS NULL; -- -- This code looks for rows that are in v1 but are not in v2 based on same user_id and as_of

[(1242,)]

-- 2)4) Are the numeric columns different between the tables? Compare the values for the same user_id.
-- I have chosen two identificators since if the aim is to compare numerical values with same date
-- same date and user, we want to find whether these transactions are same in both tables. 

SELECT
    COUNT(*) AS revenue_mismatches -- I join data from both tables and say to compare rows with same as_of & user_id
FROM players_v1 v1
JOIN players_v2 v2  -- JOIN joins only rows that are in both tables, does not compute with single rows
    ON v1.user_id = v2.user_id
   AND v1.as_of = v2.as_of
WHERE v1.revenue IS DISTINCT FROM v2.revenue;  -- looks only for rows that are distinct

[(205609,)]

SELECT COUNT(*)
FROM players_v1 v1
JOIN players_v2 v2
ON v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.deposits IS DISTINCT FROM v2.deposits;  -- compares how many deposit data from same id and same time are different when comparing 2 datasets

[(205610,)]

SELECT COUNT(*)
FROM players_v1 v1
JOIN players_v2 v2
ON v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.first_deposit_amount IS DISTINCT FROM v2.first_deposit_amount; -- compares how many deposit amount data from same id and same time are different when comparing 2 datasets

[(205610,)]

SELECT COUNT(*)
FROM players_v1 v1
JOIN players_v2 v2
ON v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.total_net_revenue IS DISTINCT FROM v2.total_net_revenue;
-- compares how many total_net_revenue from same id and same time are different when comparing 2 datasets
[(205610,)]

SELECT COUNT(*)
FROM players_v1 v1
JOIN players_v2 v2
ON v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.sportsbook_net_revenue IS DISTINCT FROM v2.sportsbook_net_revenue;
-- compares how many sportsbook_revenue data from same id and same time are different when comparing 2 datasets
[(205610,)]

SELECT COUNT(*)
FROM players_v1 v1
JOIN players_v2 v2
ON v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.sports_bets_turnover IS DISTINCT FROM v2.sports_bets_turnover;
-- compares how many sports_bets_turnover data from same id and same time are different when comparing 2 datasets
[(205610,)]

-- All numeric columns differ for almost all matched rows. This suggests a systemic issue rather than random error. 
-- Possible explanations: different aggregation logic, currency conversion, scaling factor 
-- 2)5) Are date and text columns consistent?
-- We already know this, second table has problem with years, so I will verify

SELECT COUNT(*) AS inconsistent_signup_year
FROM players_v2  
WHERE signup_year != EXTRACT(YEAR FROM signup_date); -- compare whether sign up year is in agreement with sign up date

[(205070,)]

-- Now lets verify whether there is inconsistent first deposit year
-- Meaning first deposit year < first signup year

SELECT COUNT(*) AS inconsistent_first_deposit_year
FROM players_v1 
WHERE first_deposit_year != EXTRACT(YEAR FROM first_deposit_date);

SELECT COUNT(*) AS inconsistent_first_deposit_year
FROM players_v2
WHERE first_deposit_year != EXTRACT(YEAR FROM first_deposit_date);

SELECT COUNT(*) AS invalid_deposit_before_signup
FROM players_v1
WHERE first_deposit_date < signup_date;

SELECT COUNT(*) AS invalid_deposit_before_signup
FROM players_v2
WHERE first_deposit_date < signup_date;

[(0,)] 
[(0,)] 
[(0,)] 
[(0,)] 

-- There may also be problem with NULL value at first deposit amount if then is generated revenue or some income

SELECT COUNT(*) AS invalid_first_deposit_amount
FROM players_v2
WHERE first_deposit_amount=0 
    AND (deposits > 0
    OR revenue <> 0
    OR sports_bets_turnover > 0);

[(20581,)] -- for _v1 it is [(0,)]
-- This inclines that there may be issue with tracking first deposit amounts in _v2 table. Or there was some bonus from company or some action.

-- 2)6) Are relations between columns correct? - chech whether tracker_id and tracker_name are same in both tables

SELECT COUNT(*) AS inconsistent_tracker_ids
FROM (
    SELECT tracker_id
    FROM players_v1 
    GROUP BY tracker_id
    HAVING COUNT(DISTINCT tracker_name) > 1
);

SELECT COUNT(*) AS inconsistent_tracker_ids
FROM (
    SELECT tracker_id
    FROM players_v2
    GROUP BY tracker_id
    HAVING COUNT(DISTINCT tracker_name) > 1
);

SELECT COUNT(*) AS inconsistent_tracker_names
FROM (
    SELECT tracker_name
    FROM players_v1 
    GROUP BY tracker_name
    HAVING COUNT(DISTINCT tracker_id) > 1
);

SELECT COUNT(*) AS inconsistent_tracker_names
FROM (
    SELECT tracker_name
    FROM players_v2
    GROUP BY tracker_name
    HAVING COUNT(DISTINCT tracker_id) > 1
);

SELECT COUNT(*) AS tracker_mismatches
FROM players_v1 v1
JOIN players_v2 v2
ON v1.tracker_id = v2.tracker_id
AND v1.user_id = v2.user_id
AND v1.as_of = v2.as_of
WHERE v1.tracker_name IS DISTINCT FROM v2.tracker_name;

[(2,)] 
[(29,)]
[(71,)] 
[(69,)]
[(418,)]

-- So people with same tracker_id in v1 have a different tracker_name in v2: 2
-- people with same tracker_id in v2 have a different tracker_name in v1: 29
-- People with the same name in v1 have different tracker_id in v2: 71
-- People with the same name in v2 have different tracker_id in v1: 71
--People with same as_of, tracker_id and user_id with different tracker_name when comparing 2 tables: 418


