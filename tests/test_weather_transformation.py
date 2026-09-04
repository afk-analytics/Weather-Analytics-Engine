from src.ingestion.weather_ingestion import read_station_file
from src.transformation.weather_transformation import transform_weather_data


FILE_PATH = "data/raw/CardiffButePark.txt"


def test_transformation_adds_expected_columns():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    expected_columns = {
        "date",
        "mean_temperature",
        "month_name",
        "season",
        "rainy_month",
        "temperature_range"
    }

    assert expected_columns.issubset(transformed_df.columns)


def test_date_is_created_correctly():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    assert transformed_df.loc[0, "date"].year == 1977
    assert transformed_df.loc[0, "date"].month == 9
    assert transformed_df.loc[0, "date"].day == 1


def test_mean_temperature_is_correct():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    expected_mean = (
        transformed_df.loc[0, "tmax"] +
        transformed_df.loc[0, "tmin"]
    ) / 2

    assert transformed_df.loc[0, "mean_temperature"] == expected_mean


def test_temperature_range_is_correct():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    expected_range = (
        transformed_df.loc[0, "tmax"] -
        transformed_df.loc[0, "tmin"]
    )

    assert transformed_df.loc[0, "temperature_range"] == expected_range


def test_season_mapping_is_correct():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    december_row = transformed_df[
        (transformed_df["year"] == 1977) &
        (transformed_df["month"] == 12)
    ].iloc[0]

    assert december_row["season"] == "Winter"


def test_month_name_is_correct():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    september_row = transformed_df[
        (transformed_df["year"] == 1977) &
        (transformed_df["month"] == 9)
    ].iloc[0]

    assert september_row["month_name"] == "September"


def test_transformed_data_is_sorted_chronologically():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    assert transformed_df["date"].is_monotonic_increasing


def test_row_count_is_preserved():
    raw_df = read_station_file(FILE_PATH)

    transformed_df = transform_weather_data(raw_df)

    assert len(transformed_df) == len(raw_df)