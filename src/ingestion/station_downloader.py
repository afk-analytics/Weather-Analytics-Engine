from pathlib import Path
import re
from urllib.parse import urljoin

import requests


STATION_PAGE_URL = (
    "https://www.metoffice.gov.uk/research/climate/"
    "maps-and-data/historic-station-data"
)

RAW_DATA_DIRECTORY = Path("data/raw/met_office")


def get_station_urls() -> list[str]:
    """
    Discover all historic station data files linked
    from the Met Office historic station page.
    """

    response = requests.get(
        STATION_PAGE_URL,
        timeout=30
    )

    response.raise_for_status()

    station_links = re.findall(
        r'href=["\']([^"\']*stationdata/[^"\']+data\.txt)["\']',
        response.text,
        flags=re.IGNORECASE
    )

    station_urls = [
        urljoin(STATION_PAGE_URL, link)
        for link in station_links
    ]

    return sorted(set(station_urls))


def download_station_files(
    station_urls: list[str]
) -> None:
    """
    Download all discovered station data files.
    """

    RAW_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    for url in station_urls:

        file_name = url.split("/")[-1]

        output_path = (
            RAW_DATA_DIRECTORY / file_name
        )

        print(f"Downloading: {file_name}")

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        output_path.write_text(
            response.text,
            encoding="utf-8"
        )


if __name__ == "__main__":

    urls = get_station_urls()

    print(
        f"Historic station files discovered: {len(urls)}"
    )

    download_station_files(urls)

    print(
        f"Downloaded {len(urls)} station files successfully."
    )