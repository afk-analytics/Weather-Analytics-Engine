from pathlib import Path

import pandas as pd

from src.ingestion.weather_ingestion import read_station_file


TEST_FILE = Path(
    "data/raw/met_office/cardiffdata.txt"
)


def test_station_file_loads():
    data = read_station_file(TEST_FILE)

    assert isinstance(data, pd.DataFrame)
    assert len(data) > 0


def test_expected_columns_exist():
    data = read_station_file(TEST_FILE)

    expected_columns = {
        "year",
        "month",
        "tmax",
        "tmin",
        "af",
        "rain",
        "sun",
        "status",
        "tmax_estimated",
        "tmin_estimated",
        "af_estimated",
        "rain_estimated",
        "sun_estimated",
        "sun_automatic_sensor"
    }

    assert expected_columns.issubset(
        set(data.columns)
    )


def test_month_values_are_valid():
    data = read_station_file(TEST_FILE)

    valid_months = (
        data["month"]
        .dropna()
        .between(1, 12)
        .all()
    )

    assert valid_months


def test_year_values_are_valid():
    data = read_station_file(TEST_FILE)

    valid_years = (
        data["year"]
        .dropna()
        .ge(1900)
        .all()
    )

    assert valid_years


def test_rainfall_is_non_negative():
    data = read_station_file(TEST_FILE)

    valid_rainfall = (
        data["rain"]
        .dropna()
        .ge(0)
        .all()
    )

    assert valid_rainfall


def test_air_frost_is_non_negative():
    data = read_station_file(TEST_FILE)

    valid_frost = (
        data["af"]
        .dropna()
        .ge(0)
        .all()
    )

    assert valid_frost


def test_tmax_is_not_lower_than_tmin():
    data = read_station_file(TEST_FILE)

    valid_rows = data[
        data["tmax"].notna()
        & data["tmin"].notna()
    ]

    assert (
        valid_rows["tmax"]
        >= valid_rows["tmin"]
    ).all()


def test_year_month_is_unique():
    data = read_station_file(TEST_FILE)

    duplicate_count = (
        data
        .duplicated(
            subset=[
                "year",
                "month"
            ]
        )
        .sum()
    )

    assert duplicate_count == 0


def test_quality_flags_are_boolean():
    data = read_station_file(TEST_FILE)

    quality_columns = [
        "tmax_estimated",
        "tmin_estimated",
        "af_estimated",
        "rain_estimated",
        "sun_estimated",
        "sun_automatic_sensor"
    ]

    for column in quality_columns:

        assert pd.api.types.is_bool_dtype(
            data[column]
        )