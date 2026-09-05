import pandas as pd
from sqlalchemy import text

from src.config.database import get_engine
from src.ingestion.weather_ingestion import read_station_file
from src.transformation.weather_transformation import transform_weather_data


def prepare_for_database(data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare transformed weather data for the PostgreSQL schema.
    """

    df = data.copy()

    df = df.rename(
        columns={
            "date": "observation_date",
            "af": "air_frost_days",
            "rain": "rainfall_mm",
            "sun": "sunshine_hours",
            "rain_estimated": "rainfall_estimated",
            "sun_estimated": "sunshine_estimated"
        }
    )

    database_columns = [
        "observation_date",
        "year",
        "month",
        "tmax",
        "tmin",
        "mean_temperature",
        "temperature_range",
        "air_frost_days",
        "rainfall_mm",
        "sunshine_hours",
        "month_name",
        "season",
        "status",
        "tmax_estimated",
        "tmin_estimated",
        "rainfall_estimated",
        "sunshine_estimated"
    ]

    df = df[database_columns]

    # Convert pandas missing values to Python None
    # so PostgreSQL stores them as NULL
    df = df.astype(object).where(pd.notna(df), None)

    return df


def load_weather_data(data: pd.DataFrame) -> None:
    """
    Insert new weather observations and update existing ones.

    The unique year/month constraint determines whether
    PostgreSQL inserts a new row or updates an existing row.
    """

    engine = get_engine()

    upsert_query = text(
        """
        INSERT INTO weather_observations (
            observation_date,
            year,
            month,
            tmax,
            tmin,
            mean_temperature,
            temperature_range,
            air_frost_days,
            rainfall_mm,
            sunshine_hours,
            month_name,
            season,
            status,
            tmax_estimated,
            tmin_estimated,
            rainfall_estimated,
            sunshine_estimated
        )
        VALUES (
            :observation_date,
            :year,
            :month,
            :tmax,
            :tmin,
            :mean_temperature,
            :temperature_range,
            :air_frost_days,
            :rainfall_mm,
            :sunshine_hours,
            :month_name,
            :season,
            :status,
            :tmax_estimated,
            :tmin_estimated,
            :rainfall_estimated,
            :sunshine_estimated
        )

        ON CONFLICT (year, month)

        DO UPDATE SET
            observation_date = EXCLUDED.observation_date,
            tmax = EXCLUDED.tmax,
            tmin = EXCLUDED.tmin,
            mean_temperature = EXCLUDED.mean_temperature,
            temperature_range = EXCLUDED.temperature_range,
            air_frost_days = EXCLUDED.air_frost_days,
            rainfall_mm = EXCLUDED.rainfall_mm,
            sunshine_hours = EXCLUDED.sunshine_hours,
            month_name = EXCLUDED.month_name,
            season = EXCLUDED.season,
            status = EXCLUDED.status,
            tmax_estimated = EXCLUDED.tmax_estimated,
            tmin_estimated = EXCLUDED.tmin_estimated,
            rainfall_estimated = EXCLUDED.rainfall_estimated,
            sunshine_estimated = EXCLUDED.sunshine_estimated;
        """
    )

    records = data.to_dict(orient="records")

    with engine.begin() as connection:
        connection.execute(
            upsert_query,
            records
        )


def get_database_row_count() -> int:
    """
    Return the number of records currently stored
    in weather_observations.
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM weather_observations
                """
            )
        )

        return result.scalar_one()


if __name__ == "__main__":

    file_path = "data/raw/CardiffButePark.txt"

    raw_df = read_station_file(file_path)

    transformed_df = transform_weather_data(raw_df)

    database_df = prepare_for_database(transformed_df)

    print(f"Records ready to load: {len(database_df)}")

    load_weather_data(database_df)

    row_count = get_database_row_count()

    print(f"Database row count: {row_count}")
    print("Weather data loaded successfully.")