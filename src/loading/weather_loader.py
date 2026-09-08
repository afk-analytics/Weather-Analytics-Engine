from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.config.database import get_engine
from src.ingestion.station_metadata import read_station_metadata
from src.ingestion.weather_ingestion import read_station_file
from src.transformation.weather_transformation import transform_weather_data


STATION_DIRECTORY = Path(
    "data/raw/met_office"
)


def prepare_for_database(
    data: pd.DataFrame,
    station_name: str,
    latitude: float,
    longitude: float,
    elevation_metres: float
) -> pd.DataFrame:
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

    df["station_name"] = station_name
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["elevation_metres"] = elevation_metres

    database_columns = [
        "observation_date",
        "station_name",
        "latitude",
        "longitude",
        "elevation_metres",
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

    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    return df


def load_weather_data(
    data: pd.DataFrame
) -> None:
    """
    Insert new weather observations and
    update existing observations.
    """

    engine = get_engine()

    upsert_query = text(
        """
        INSERT INTO weather_observations (
            observation_date,
            station_name,
            latitude,
            longitude,
            elevation_metres,
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
            :station_name,
            :latitude,
            :longitude,
            :elevation_metres,
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

        ON CONFLICT (
            station_name,
            year,
            month
        )

        DO UPDATE SET
            observation_date =
                EXCLUDED.observation_date,

            latitude =
                EXCLUDED.latitude,

            longitude =
                EXCLUDED.longitude,

            elevation_metres =
                EXCLUDED.elevation_metres,

            tmax =
                EXCLUDED.tmax,

            tmin =
                EXCLUDED.tmin,

            mean_temperature =
                EXCLUDED.mean_temperature,

            temperature_range =
                EXCLUDED.temperature_range,

            air_frost_days =
                EXCLUDED.air_frost_days,

            rainfall_mm =
                EXCLUDED.rainfall_mm,

            sunshine_hours =
                EXCLUDED.sunshine_hours,

            month_name =
                EXCLUDED.month_name,

            season =
                EXCLUDED.season,

            status =
                EXCLUDED.status,

            tmax_estimated =
                EXCLUDED.tmax_estimated,

            tmin_estimated =
                EXCLUDED.tmin_estimated,

            rainfall_estimated =
                EXCLUDED.rainfall_estimated,

            sunshine_estimated =
                EXCLUDED.sunshine_estimated;
        """
    )

    records = data.to_dict(
        orient="records"
    )

    with engine.begin() as connection:

        connection.execute(
            upsert_query,
            records
        )


def get_database_row_count() -> int:
    """
    Return total observations currently
    stored in PostgreSQL.
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

    station_files = sorted(
        STATION_DIRECTORY.glob("*.txt")
    )

    print(
        f"Station files discovered: "
        f"{len(station_files)}"
    )

    for station_file in station_files:

        metadata = read_station_metadata(
            station_file
        )

        print(
            f"Processing: "
            f"{metadata['station_name']}"
        )

        raw_df = read_station_file(
            station_file
        )

        transformed_df = (
            transform_weather_data(
                raw_df
            )
        )

        database_df = (
            prepare_for_database(
                transformed_df,
                metadata["station_name"],
                metadata["latitude"],
                metadata["longitude"],
                metadata["elevation_metres"]
            )
        )

        print(
            f"Records ready to load: "
            f"{len(database_df)}"
        )

        load_weather_data(
            database_df
        )

        print(
            f"{metadata['station_name']} "
            f"loaded successfully."
        )

    row_count = (
        get_database_row_count()
    )

    print(
        f"Database row count: "
        f"{row_count}"
    )

    print(
        "All historic weather stations "
        "loaded successfully."
    )