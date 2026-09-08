-- ============================================================
-- Weather Analytics Engine
-- Station-aware analytical queries
-- ============================================================


-- ============================================================
-- 1. Annual weather summary by station
-- ============================================================

SELECT
    ws.display_station_name AS station_name,
    wo.year,
    ROUND(
        AVG(wo.mean_temperature),
        2
    ) AS average_temperature,
    ROUND(
        SUM(wo.rainfall_mm),
        2
    ) AS total_rainfall_mm,
    SUM(
        wo.air_frost_days
    ) AS total_frost_days,
    ROUND(
        SUM(wo.sunshine_hours),
        2
    ) AS total_sunshine_hours
FROM weather_observations AS wo
JOIN weather_stations AS ws
    ON wo.station_id = ws.station_id
GROUP BY
    ws.display_station_name,
    wo.year
ORDER BY
    ws.display_station_name,
    wo.year;


-- ============================================================
-- 2. Annual temperature trend by station
-- ============================================================

SELECT
    ws.display_station_name AS station_name,
    wo.year,
    ROUND(
        AVG(wo.mean_temperature),
        2
    ) AS average_temperature
FROM weather_observations AS wo
JOIN weather_stations AS ws
    ON wo.station_id = ws.station_id
WHERE wo.mean_temperature IS NOT NULL
GROUP BY
    ws.display_station_name,
    wo.year
ORDER BY
    ws.display_station_name,
    wo.year;


-- ============================================================
-- 3. Monthly weather averages by station
-- ============================================================

SELECT
    ws.display_station_name AS station_name,
    wo.month,
    wo.month_name,
    ROUND(
        AVG(wo.mean_temperature),
        2
    ) AS average_temperature,
    ROUND(
        AVG(wo.rainfall_mm),
        2
    ) AS average_rainfall_mm,
    ROUND(
        AVG(wo.sunshine_hours),
        2
    ) AS average_sunshine_hours,
    ROUND(
        AVG(wo.air_frost_days),
        2
    ) AS average_frost_days
FROM weather_observations AS wo
JOIN weather_stations AS ws
    ON wo.station_id = ws.station_id
GROUP BY
    ws.display_station_name,
    wo.month,
    wo.month_name
ORDER BY
    ws.display_station_name,
    wo.month;


-- ============================================================
-- 4. Year-on-year temperature change
-- ============================================================

WITH annual_temperature AS (

    SELECT
        wo.station_id,
        ws.display_station_name AS station_name,
        wo.year,
        AVG(
            wo.mean_temperature
        ) AS average_temperature
    FROM weather_observations AS wo
    JOIN weather_stations AS ws
        ON wo.station_id = ws.station_id
    WHERE wo.mean_temperature IS NOT NULL
    GROUP BY
        wo.station_id,
        ws.display_station_name,
        wo.year

),

temperature_change AS (

    SELECT
        station_id,
        station_name,
        year,
        average_temperature,
        LAG(
            average_temperature
        ) OVER (
            PARTITION BY station_id
            ORDER BY year
        ) AS previous_year_temperature
    FROM annual_temperature

)

SELECT
    station_name,
    year,
    ROUND(
        average_temperature,
        2
    ) AS average_temperature,
    ROUND(
        previous_year_temperature,
        2
    ) AS previous_year_temperature,
    ROUND(
        average_temperature
        - previous_year_temperature,
        2
    ) AS year_on_year_change
FROM temperature_change
ORDER BY
    station_name,
    year;


-- ============================================================
-- 5. Hottest and coldest years by station
-- ============================================================

WITH annual_temperature AS (

    SELECT
        wo.station_id,
        ws.display_station_name AS station_name,
        wo.year,
        AVG(
            wo.mean_temperature
        ) AS average_temperature
    FROM weather_observations AS wo
    JOIN weather_stations AS ws
        ON wo.station_id = ws.station_id
    WHERE wo.mean_temperature IS NOT NULL
    GROUP BY
        wo.station_id,
        ws.display_station_name,
        wo.year

),

ranked_years AS (

    SELECT
        station_id,
        station_name,
        year,
        average_temperature,

        RANK() OVER (
            PARTITION BY station_id
            ORDER BY average_temperature DESC
        ) AS hottest_year_rank,

        RANK() OVER (
            PARTITION BY station_id
            ORDER BY average_temperature ASC
        ) AS coldest_year_rank

    FROM annual_temperature

)

SELECT
    station_name,
    year,
    ROUND(
        average_temperature,
        2
    ) AS average_temperature,
    hottest_year_rank,
    coldest_year_rank
FROM ranked_years
WHERE
    hottest_year_rank <= 5
    OR coldest_year_rank <= 5
ORDER BY
    station_name,
    average_temperature DESC;


-- ============================================================
-- 6. Wettest years by station
-- ============================================================

WITH annual_rainfall AS (

    SELECT
        wo.station_id,
        ws.display_station_name AS station_name,
        wo.year,
        SUM(
            wo.rainfall_mm
        ) AS total_rainfall_mm
    FROM weather_observations AS wo
    JOIN weather_stations AS ws
        ON wo.station_id = ws.station_id
    WHERE wo.rainfall_mm IS NOT NULL
    GROUP BY
        wo.station_id,
        ws.display_station_name,
        wo.year

),

ranked_rainfall AS (

    SELECT
        station_id,
        station_name,
        year,
        total_rainfall_mm,

        RANK() OVER (
            PARTITION BY station_id
            ORDER BY total_rainfall_mm DESC
        ) AS wettest_year_rank

    FROM annual_rainfall

)

SELECT
    station_name,
    year,
    ROUND(
        total_rainfall_mm,
        2
    ) AS total_rainfall_mm,
    wettest_year_rank
FROM ranked_rainfall
WHERE wettest_year_rank <= 5
ORDER BY
    station_name,
    wettest_year_rank;


-- ============================================================
-- 7. Warmest individual months by station
-- ============================================================

SELECT
    ws.display_station_name AS station_name,
    wo.observation_date,
    wo.year,
    wo.month,
    wo.month_name,
    wo.season,
    wo.tmax,
    wo.tmin,
    wo.mean_temperature,
    wo.rainfall_mm,
    wo.sunshine_hours
FROM weather_observations AS wo
JOIN weather_stations AS ws
    ON wo.station_id = ws.station_id
WHERE wo.mean_temperature IS NOT NULL
ORDER BY
    ws.display_station_name,
    wo.mean_temperature DESC,
    wo.observation_date;