import pandas as pd

from src.ingestion.weather_ingestion import read_station_file


def transform_weather_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw monthly weather observations into
    analytics-ready fields.
    """

    df = data.copy()

    # Create a proper date using the first day of each month
    df["date"] = pd.to_datetime(
        dict(
            year=df["year"],
            month=df["month"],
            day=1
        )
    )

    # Calculate mean monthly temperature
    df["mean_temperature"] = (
        df["tmax"] + df["tmin"]
    ) / 2

    # Create readable month name
    df["month_name"] = df["date"].dt.month_name()

    # Create season
    season_mapping = {
        12: "Winter",
        1: "Winter",
        2: "Winter",
        3: "Spring",
        4: "Spring",
        5: "Spring",
        6: "Summer",
        7: "Summer",
        8: "Summer",
        9: "Autumn",
        10: "Autumn",
        11: "Autumn"
    }

    df["season"] = df["month"].map(season_mapping)

    # Flag months where rainfall was recorded
    df["rainy_month"] = df["rain"].fillna(0) > 0

    # Calculate temperature range
    df["temperature_range"] = (
        df["tmax"] - df["tmin"]
    )

    # Sort chronologically
    df = df.sort_values(
        by=["year", "month"]
    ).reset_index(drop=True)

    return df


if __name__ == "__main__":

    file_path = "data/raw/CardiffButePark.txt"

    raw_df = read_station_file(file_path)

    transformed_df = transform_weather_data(raw_df)

    print("Transformed columns:")
    print(transformed_df.columns.tolist())

    print()
    print("First five transformed rows:")
    print(
        transformed_df[
            [
                "date",
                "year",
                "month",
                "month_name",
                "season",
                "tmax",
                "tmin",
                "mean_temperature",
                "temperature_range",
                "rain",
                "rainy_month"
            ]
        ].head()
    )