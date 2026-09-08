from pathlib import Path

import pandas as pd


def read_station_file(file_path: str) -> pd.DataFrame:
    """
    Read a Met Office historic monthly station data file.

    Handles:
    - Met Office metadata/header lines
    - Missing values marked as ---
    - Estimated values marked with *
    - Sunshine sensor markers marked with #
    - Provisional observations
    """

    file_path = Path(file_path)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        lines = file.readlines()

    # Find the start of the observation table
    header_index = next(
        i for i, line in enumerate(lines)
        if line.strip().startswith("yyyy")
    )

    # Skip the column headings and units row
    data_lines = lines[header_index + 2:]

    records = []

    for line in data_lines:

        parts = line.split()

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
            "status": (
                " ".join(parts[7:])
                if len(parts) > 7
                else None
            )
        }

        records.append(record)

    data = pd.DataFrame(records)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    data = data.replace(
        "---",
        pd.NA
    )

    # --------------------------------------------------------
    # Estimated values
    #
    # Met Office uses * to indicate estimated observations.
    # Preserve this information before removing the marker.
    # --------------------------------------------------------

    estimated_columns = [
        "tmax",
        "tmin",
        "af",
        "rain",
        "sun"
    ]

    for column in estimated_columns:

        data[f"{column}_estimated"] = (
            data[column]
            .astype("string")
            .str.contains(
                r"\*",
                regex=True,
                na=False
            )
        )

        data[column] = (
            data[column]
            .astype("string")
            .str.replace(
                "*",
                "",
                regex=False
            )
        )

    # --------------------------------------------------------
    # Sunshine sensor marker
    #
    # Met Office historic files may use # to identify
    # sunshine observations recorded using an automatic
    # Kipp & Zonen sensor.
    #
    # Preserve the marker as a boolean field before removing
    # it from the numeric value.
    # --------------------------------------------------------

    data["sun_automatic_sensor"] = (
        data["sun"]
        .astype("string")
        .str.contains(
            "#",
            regex=False,
            na=False
        )
    )

    data["sun"] = (
        data["sun"]
        .astype("string")
        .str.replace(
            "#",
            "",
            regex=False
        )
    )

    # --------------------------------------------------------
    # Convert observation fields to numeric values
    # --------------------------------------------------------

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

    # Use nullable integer types where appropriate
    data["year"] = (
        data["year"]
        .astype("Int64")
    )

    data["month"] = (
        data["month"]
        .astype("Int64")
    )

    data["af"] = (
        data["af"]
        .astype("Int64")
    )

    return data