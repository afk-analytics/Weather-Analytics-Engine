-- ============================================================
-- Weather Analytics Engine
-- Analytical SQL Queries
-- ============================================================

-- 1. Annual weather summary
-- Provides yearly averages/totals for temperature, rainfall,
-- frost and sunshine.

SELECT
    year,
    ROUND(AVG(mean_temperature), 2) AS avg_temperature_c,
    ROUND(AVG(tmax), 2) AS avg_max_temperature_c,
    ROUND(AVG(tmin), 2) AS avg_min_temperature_c,
    ROUND(SUM(rainfall_mm), 2) AS total_rainfall_mm,
    SUM(air_frost_days) AS total_air_frost_days,
    ROUND(SUM(sunshine_hours), 2) AS total_sunshine_hours
FROM weather_observations
GROUP BY year
ORDER BY year;

-- 2. Annual temperature trend
-- Shows how average annual temperature changes over time.

SELECT
    year,
    ROUND(AVG(mean_temperature), 2) AS avg_temperature_c
FROM weather_observations
GROUP BY year
ORDER BY year;

-- 3. Monthly weather averages
-- Shows typical weather conditions for each month of the year.

SELECT
    month,
    month_name,
    ROUND(AVG(mean_temperature), 2) AS avg_temperature_c,
    ROUND(AVG(rainfall_mm), 2) AS avg_rainfall_mm,
    ROUND(AVG(air_frost_days), 2) AS avg_air_frost_days,
    ROUND(AVG(sunshine_hours), 2) AS avg_sunshine_hours
FROM weather_observations
GROUP BY month, month_name
ORDER BY month;

-- 4. Year-on-year temperature change
-- Compares each year's average temperature with the previous year.

WITH annual_temperature AS (
    SELECT
        year,
        AVG(mean_temperature) AS avg_temperature_c
    FROM weather_observations
    GROUP BY year
)

SELECT
    year,
    ROUND(avg_temperature_c, 2) AS avg_temperature_c,
    ROUND(
        avg_temperature_c
        - LAG(avg_temperature_c) OVER (ORDER BY year),
        2
    ) AS year_on_year_change_c
FROM annual_temperature
ORDER BY year;

-- 5. Hottest and coldest years
-- Ranks years by average annual temperature.

WITH annual_temperature AS (
    SELECT
        year,
        AVG(mean_temperature) AS avg_temperature_c
    FROM weather_observations
    GROUP BY year
)

SELECT
    year,
    ROUND(avg_temperature_c, 2) AS avg_temperature_c,
    RANK() OVER (
        ORDER BY avg_temperature_c DESC
    ) AS hottest_year_rank,
    RANK() OVER (
        ORDER BY avg_temperature_c ASC
    ) AS coldest_year_rank
FROM annual_temperature
ORDER BY avg_temperature_c DESC;

-- 6. Wettest years
-- Ranks years by total annual rainfall.

WITH annual_rainfall AS (
    SELECT
        year,
        SUM(rainfall_mm) AS total_rainfall_mm
    FROM weather_observations
    GROUP BY year
)

SELECT
    year,
    ROUND(total_rainfall_mm, 2) AS total_rainfall_mm,
    RANK() OVER (
        ORDER BY total_rainfall_mm DESC
    ) AS wettest_year_rank
FROM annual_rainfall
ORDER BY total_rainfall_mm DESC;

-- 7. Warmest individual months on record
-- Identifies the hottest monthly observations in the dataset.

SELECT
    observation_date,
    year,
    month_name,
    mean_temperature,
    tmax,
    tmin
FROM weather_observations
ORDER BY mean_temperature DESC
LIMIT 10;