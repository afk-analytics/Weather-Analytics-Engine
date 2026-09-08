-- ============================================================
-- Weather Analytics Engine
-- Analytical SQL Queries
-- ============================================================

-- 1. Annual weather summary
-- Provides yearly averages/totals for temperature, rainfall,
-- frost and sunshine.

SELECT
    station_name,
    year,
    ROUND(AVG(mean_temperature), 2) AS avg_temperature_c,
    ROUND(AVG(tmax), 2) AS avg_max_temperature_c,
    ROUND(AVG(tmin), 2) AS avg_min_temperature_c,
    ROUND(SUM(rainfall_mm), 2) AS total_rainfall_mm,
    SUM(air_frost_days) AS total_air_frost_days,
    ROUND(SUM(sunshine_hours), 2) AS total_sunshine_hours
FROM weather_observations
GROUP BY
    station_name,
    year
ORDER BY
    station_name,
    year;

-- 2. Annual temperature trend
-- Shows how average annual temperature changes over time.

SELECT
    station_name,
    year,
    ROUND(
        AVG(mean_temperature),
        2
    ) AS avg_temperature_c
FROM weather_observations
GROUP BY
    station_name,
    year
ORDER BY
    station_name,
    year;

-- 3. Monthly weather averages
-- Shows typical weather conditions for each month of the year.

SELECT
    station_name,
    month,
    month_name,
    ROUND(
        AVG(mean_temperature),
        2
    ) AS avg_temperature_c,
    ROUND(
        AVG(rainfall_mm),
        2
    ) AS avg_rainfall_mm,
    ROUND(
        AVG(air_frost_days),
        2
    ) AS avg_air_frost_days,
    ROUND(
        AVG(sunshine_hours),
        2
    ) AS avg_sunshine_hours
FROM weather_observations
GROUP BY
    station_name,
    month,
    month_name
ORDER BY
    station_name,
    month;

-- 4. Year-on-year temperature change
-- Compares each year's average temperature with the previous year.

WITH annual_temperature AS (
    SELECT
        station_name,
        year,
        AVG(mean_temperature) AS avg_temperature_c
    FROM weather_observations
    GROUP BY
        station_name,
        year
),

temperature_change AS (
    SELECT
        station_name,
        year,
        avg_temperature_c,
        LAG(avg_temperature_c) OVER (
            PARTITION BY station_name
            ORDER BY year
        ) AS previous_year_temperature
    FROM annual_temperature
)

SELECT
    station_name,
    year,
    ROUND(
        avg_temperature_c,
        2
    ) AS avg_temperature_c,
    ROUND(
        previous_year_temperature,
        2
    ) AS previous_year_temperature_c,
    ROUND(
        avg_temperature_c
        - previous_year_temperature,
        2
    ) AS year_on_year_change_c
FROM temperature_change
ORDER BY
    station_name,
    year;

-- 5. Hottest and coldest years
-- Ranks years by average annual temperature.

WITH annual_temperature AS (
    SELECT
        station_name,
        year,
        AVG(mean_temperature) AS avg_temperature_c
    FROM weather_observations
    GROUP BY
        station_name,
        year
),

ranked_years AS (
    SELECT
        station_name,
        year,
        avg_temperature_c,

        RANK() OVER (
            PARTITION BY station_name
            ORDER BY avg_temperature_c DESC
        ) AS hottest_rank,

        RANK() OVER (
            PARTITION BY station_name
            ORDER BY avg_temperature_c ASC
        ) AS coldest_rank

    FROM annual_temperature
)

SELECT
    station_name,
    year,
    ROUND(
        avg_temperature_c,
        2
    ) AS avg_temperature_c,
    hottest_rank,
    coldest_rank
FROM ranked_years
ORDER BY
    station_name,
    hottest_rank,
    year;

-- 6. Wettest years
-- Ranks years by total annual rainfall.

WITH annual_rainfall AS (
    SELECT
        station_name,
        year,
        SUM(rainfall_mm) AS total_rainfall_mm
    FROM weather_observations
    GROUP BY
        station_name,
        year
),

ranked_rainfall AS (
    SELECT
        station_name,
        year,
        total_rainfall_mm,
        RANK() OVER (
            PARTITION BY station_name
            ORDER BY total_rainfall_mm DESC
        ) AS rainfall_rank
    FROM annual_rainfall
)

SELECT
    station_name,
    year,
    ROUND(
        total_rainfall_mm,
        2
    ) AS total_rainfall_mm,
    rainfall_rank
FROM ranked_rainfall
ORDER BY
    station_name,
    rainfall_rank,
    year;

-- 7. Warmest individual months on record
-- Identifies the hottest monthly observations in the dataset.

SELECT
    station_name,
    observation_date,
    year,
    month,
    month_name,
    ROUND(
        mean_temperature,
        2
    ) AS mean_temperature_c,
    ROUND(
        tmax,
        2
    ) AS tmax_c,
    ROUND(
        tmin,
        2
    ) AS tmin_c
FROM weather_observations
WHERE mean_temperature IS NOT NULL
ORDER BY
    station_name,
    mean_temperature DESC,
    observation_date;