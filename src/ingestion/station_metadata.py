from pathlib import Path
import re


def read_station_metadata(file_path: str) -> dict:
    """
    Extract station metadata from a Met Office
    historic station data file.

    The full metadata header is searched because
    station location information can span multiple lines.
    """

    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Station name is stored on the first line
    station_name = lines[0].strip()

    # Find where the actual weather observations begin
    header_index = next(
        i for i, line in enumerate(lines)
        if line.strip().startswith("yyyy")
    )

    # Combine the complete metadata/header section
    header_text = " ".join(
        line.strip()
        for line in lines[:header_index]
    )

    # Extract latitude
    latitude_match = re.search(
        r"Lat[:\s]+(-?\d+(?:\.\d+)?)",
        header_text,
        flags=re.IGNORECASE
    )

    # Extract longitude
    longitude_match = re.search(
        r"Lon[:\s]+(-?\d+(?:\.\d+)?)",
        header_text,
        flags=re.IGNORECASE
    )

    # Extract all elevations because some stations
    # have moved during their history
    elevation_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*(?:metres|metre|m)\s+amsl",
        header_text,
        flags=re.IGNORECASE
    )

    if not latitude_match:
        raise ValueError(
            f"Latitude not found in {file_path.name}: "
            f"{header_text}"
        )

    if not longitude_match:
        raise ValueError(
            f"Longitude not found in {file_path.name}: "
            f"{header_text}"
        )

    if not elevation_matches:
        raise ValueError(
            f"Elevation not found in {file_path.name}: "
            f"{header_text}"
        )

    # If a station moved, use the latest listed elevation
    elevation = elevation_matches[-1]

    return {
        "file_path": str(file_path),
        "station_name": station_name,
        "latitude": float(latitude_match.group(1)),
        "longitude": float(longitude_match.group(1)),
        "elevation_metres": float(elevation)
    }


if __name__ == "__main__":

    station_directory = Path(
        "data/raw/met_office"
    )

    station_files = sorted(
        station_directory.glob("*.txt")
    )

    print(
        f"Station files found: {len(station_files)}"
    )

    successful_stations = 0

    for station_file in station_files:

        metadata = read_station_metadata(
            station_file
        )

        print(
            metadata["station_name"],
            metadata["latitude"],
            metadata["longitude"],
            metadata["elevation_metres"]
        )

        successful_stations += 1

    print(
        f"Metadata successfully extracted for "
        f"{successful_stations} stations."
    )