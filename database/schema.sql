-- ============================================================
-- Weather Analytics Engine
-- PostgreSQL Database Schema
-- ============================================================

-- Create table for monthly weather observations
CREATE TABLE IF NOT EXISTS weather_observations (

    observation_id BIGSERIAL PRIMARY KEY,

    observation_date DATE NOT NULL,

    year INTEGER NOT NULL,
    month INTEGER NOT NULL,

    tmax NUMERIC(5,2),
    tmin NUMERIC(5,2),
    mean_temperature NUMERIC(5,2),
    temperature_range NUMERIC(5,2),

    air_frost_days INTEGER,
    rainfall_mm NUMERIC(7,2),
    sunshine_hours NUMERIC(7,2),

    month_name VARCHAR(20),
    season VARCHAR(10),

    status VARCHAR(50),

    tmax_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    tmin_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    rainfall_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    sunshine_estimated BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT uq_weather_year_month
        UNIQUE (year, month),

    CONSTRAINT chk_month
        CHECK (month BETWEEN 1 AND 12),

    CONSTRAINT chk_rainfall
        CHECK (rainfall_mm >= 0),

    CONSTRAINT chk_air_frost
        CHECK (air_frost_days >= 0),

    CONSTRAINT chk_temperature_range
        CHECK (temperature_range >= 0),

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