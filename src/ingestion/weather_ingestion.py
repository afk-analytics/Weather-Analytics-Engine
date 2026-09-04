from pathlib import Path
import pandas as pd


def read_station_file(file_path: str) -> pd.DataFrame:
    """
    Read a Met Office historic monthly station data file.

    Handles:
    - Met Office metadata/header lines
    - Missing values marked as ---
    - Estimated values marked with *
    - Provisional observations
    """

    file_path = Path(file_path)

    # Read the file as text
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Find the actual column header
    header_index = next(
        i for i, line in enumerate(lines)
        if line.strip().startswith("yyyy")
    )

    # Data starts two lines after the column header.
    # Line 1: yyyy mm tmax tmin af rain sun
    # Line 2: degC degC days mm hours
    data_lines = lines[header_index + 2:]

    # Parse the observation rows
    records = []

    for line in data_lines:
        parts = line.split()

        # Ignore empty or malformed lines
        if len(parts) < 7:
            continue

        record = {
            "year": parts[0],
            "month": parts[1],
            "tmax": parts[2],
            "tmin": parts[3],
            "af": parts[4],
            "rain": parts[5],
            "sun": parts[6],
            "status": " ".join(parts[7:]) if len(parts) > 7 else None
        }

        records.append(record)

    data = pd.DataFrame(records)

    # Convert Met Office missing-value markers to pandas NA
    data = data.replace("---", pd.NA)

    # Create estimated-data flags
    for column in ["tmax", "tmin", "rain", "sun"]:

        data[f"{column}_estimated"] = (
            data[column]
            .astype("string")
            .str.endswith("*", na=False)
        )

        # Remove the * marker from the actual value
        data[column] = (
            data[column]
            .astype("string")
            .str.replace("*", "", regex=False)
        )

    # Convert columns to numeric values
    numeric_columns = [
        "year",
        "month",
        "tmax",
        "tmin",
        "af",
        "rain",
        "sun"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Use nullable integer types
    data["year"] = data["year"].astype("Int64")
    data["month"] = data["month"].astype("Int64")
    data["af"] = data["af"].astype("Int64")

    return data


if __name__ == "__main__":

    file_path = "data/raw/CardiffButePark.txt"

    df = read_station_file(file_path)

    # --------------------------------------------------
    # BASIC DATA CHECKS
    # --------------------------------------------------

    print("First five rows:")
    print(df.head())

    print()
    print("Last ten rows:")
    print(df.tail(10))

    print()
    print("Data shape:")
    print(df.shape)

    # --------------------------------------------------
    # MISSING VALUE CHECKS
    # --------------------------------------------------

    print()
    print("Missing values:")
    print(df.isna().sum())

    # --------------------------------------------------
    # ESTIMATED VALUE CHECKS
    # --------------------------------------------------

    print()
    print("Estimated values:")
    print(
        df[
            [
                "tmax_estimated",
                "tmin_estimated",
                "rain_estimated",
                "sun_estimated"
            ]
        ].sum()
    )

    # --------------------------------------------------
    # INVESTIGATE MISSING AIR FROST DATA
    # --------------------------------------------------

    print()
    print("Missing air frost observations:")

    print(
        df.loc[
            df["af"].isna(),
            ["year", "month", "af"]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # INVESTIGATE MISSING SUNSHINE DATA
    # --------------------------------------------------

    print()
    print("Missing sunshine observations by year:")

    print(
        df.loc[df["sun"].isna()]
        .groupby("year")
        .size()
        .to_string()
    )