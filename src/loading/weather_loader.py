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


def upsert_station(
    station_name: str,
    latitude: float,
    longitude: float,
    elevation_metres: float
) -> int:
    """
    Insert or update a weather station and return its station_id.
    """

    engine = get_engine()

    station_query = text(
        """
        INSERT INTO weather_stations (
            source_station_name,
            display_station_name,
            latitude,
            longitude,
            elevation_metres
        )
        VALUES (
            :source_station_name,
            :display_station_name,
            :latitude,
            :longitude,
            :elevation_metres
        )

        ON CONFLICT (
            source_station_name
        )

        DO UPDATE SET
            latitude =
                EXCLUDED.latitude,

            longitude =
                EXCLUDED.longitude,

            elevation_metres =
                EXCLUDED.elevation_metres

        RETURNING station_id;
        """
    )

    station_record = {
        "source_station_name": station_name,
        "display_station_name": station_name,
        "latitude": latitude,
        "longitude": longitude,
        "elevation_metres": elevation_metres
    }

    with engine.begin() as connection:

        result = connection.execute(
            station_query,
            station_record
        )

        station_id = result.scalar_one()

    return station_id


def prepare_for_database(
    data: pd.DataFrame,
    station_id: int
) -> pd.DataFrame:
    """
    Prepare transformed weather data for the PostgreSQL fact table.
    """

    df = data.copy()

    df = df.rename(
        columns={
            "date": "observation_date",
            "af": "air_frost_days",
            "rain": "rainfall_mm",
            "sun": "sunshine_hours",
            "af_estimated": "air_frost_estimated",
            "rain_estimated": "rainfall_estimated",
            "sun_estimated": "sunshine_estimated",
            "sun_automatic_sensor": "sunshine_automatic_sensor"
        }
    )

    df["station_id"] = station_id

    database_columns = [
        "observation_date",
        "station_id",
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
        "air_frost_estimated",
        "rainfall_estimated",
        "sunshine_estimated",
        "sunshine_automatic_sensor"
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
    Insert new weather observations and update existing observations.
    """

    engine = get_engine()

    upsert_query = text(
        """
        INSERT INTO weather_observations (
            observation_date,
            station_id,
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
            air_frost_estimated,
            rainfall_estimated,
            sunshine_estimated,
            sunshine_automatic_sensor
        )
        VALUES (
            :observation_date,
            :station_id,
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
            :air_frost_estimated,
            :rainfall_estimated,
            :sunshine_estimated,
            :sunshine_automatic_sensor
        )

        ON CONFLICT (
            station_id,
            year,
            month
        )

        DO UPDATE SET
            observation_date =
                EXCLUDED.observation_date,

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

            air_frost_estimated =
                EXCLUDED.air_frost_estimated,

            rainfall_estimated =
                EXCLUDED.rainfall_estimated,

            sunshine_estimated =
                EXCLUDED.sunshine_estimated,

            sunshine_automatic_sensor =
                EXCLUDED.sunshine_automatic_sensor;
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
    Return the total number of weather observations in PostgreSQL.
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

        station_id = upsert_station(
            metadata["station_name"],
            metadata["latitude"],
            metadata["longitude"],
            metadata["elevation_metres"]
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
                station_id
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