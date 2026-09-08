-- ============================================================
-- Weather Analytics Engine
-- PostgreSQL Database Schema
-- ============================================================
-- ============================================================
-- Weather station dimension
-- ============================================================

CREATE TABLE IF NOT EXISTS weather_stations (

    station_id BIGSERIAL PRIMARY KEY,

    source_station_name VARCHAR(150) NOT NULL UNIQUE,

    display_station_name VARCHAR(100) NOT NULL,

    latitude NUMERIC(8,5),

    longitude NUMERIC(8,5),

    elevation_metres NUMERIC(7,2),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Weather observations fact table
-- ============================================================

CREATE TABLE IF NOT EXISTS weather_observations (

    observation_id BIGSERIAL PRIMARY KEY,

    observation_date DATE NOT NULL,

    -- Weather station relationship
    station_id BIGINT NOT NULL,

    CONSTRAINT fk_weather_station
        FOREIGN KEY (station_id)
        REFERENCES weather_stations(station_id),

    -- Observation period
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,

    -- Temperature
    tmax NUMERIC(5,2),
    tmin NUMERIC(5,2),
    mean_temperature NUMERIC(5,2),
    temperature_range NUMERIC(5,2),

    -- Weather measurements
    air_frost_days INTEGER,
    rainfall_mm NUMERIC(7,2),
    sunshine_hours NUMERIC(7,2),

    -- Analytical fields
    month_name VARCHAR(20),
    season VARCHAR(10),

    -- Data quality / status
    status VARCHAR(50),

    tmax_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    tmin_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    air_frost_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    rainfall_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    sunshine_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    sunshine_automatic_sensor BOOLEAN NOT NULL DEFAULT FALSE,

    -- One observation per station, year and month
    CONSTRAINT uq_weather_station_year_month
        UNIQUE (
            station_id,
            year,
            month
        ),

    -- Data quality constraints
    CONSTRAINT chk_month
        CHECK (
            month BETWEEN 1 AND 12
        ),

    CONSTRAINT chk_rainfall
        CHECK (
            rainfall_mm >= 0
        ),

    CONSTRAINT chk_air_frost
        CHECK (
            air_frost_days >= 0
        ),

    CONSTRAINT chk_temperature_range
        CHECK (
            temperature_range >= 0
        ),

    CONSTRAINT chk_season
        CHECK (
            season IN (
                'Winter',
                'Spring',
                'Summer',
                'Autumn'
            )
        )
);