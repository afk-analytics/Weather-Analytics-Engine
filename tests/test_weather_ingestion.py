from src.ingestion.weather_ingestion import read_station_file


FILE_PATH = "data/raw/CardiffButePark.txt"


def test_file_loads():
    df = read_station_file(FILE_PATH)

    assert not df.empty


def test_expected_columns_exist():
    df = read_station_file(FILE_PATH)

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
        "rain_estimated",
        "sun_estimated"
    }

    assert expected_columns.issubset(df.columns)


def test_month_values_are_valid():
    df = read_station_file(FILE_PATH)

    assert df["month"].between(1, 12).all()


def test_year_values_are_valid():
    df = read_station_file(FILE_PATH)

    assert (df["year"] >= 1900).all()


def test_rainfall_is_not_negative():
    df = read_station_file(FILE_PATH)

    assert (df["rain"].dropna() >= 0).all()


def test_air_frost_is_not_negative():
    df = read_station_file(FILE_PATH)

    assert (df["af"].dropna() >= 0).all()


def test_max_temperature_is_not_lower_than_min_temperature():
    df = read_station_file(FILE_PATH)

    valid_rows = df[
        df["tmax"].notna() &
        df["tmin"].notna()
    ]

    assert (
        valid_rows["tmax"] >= valid_rows["tmin"]
    ).all()


def test_year_month_combination_is_unique():
    df = read_station_file(FILE_PATH)

    duplicates = df.duplicated(
        subset=["year", "month"]
    )

    assert not duplicates.any()


def test_estimated_flags_are_boolean():
    df = read_station_file(FILE_PATH)

    estimated_columns = [
        "tmax_estimated",
        "tmin_estimated",
        "rain_estimated",
        "sun_estimated"
    ]

    for column in estimated_columns:
        assert df[column].isin([True, False]).all()