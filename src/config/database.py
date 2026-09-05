import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load environment variables from .env
load_dotenv()


def get_database_url() -> str:
    """
    Build the PostgreSQL connection URL using
    credentials stored in the .env file.
    """

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Check that all required environment variables exist
    required_variables = {
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_NAME": database,
        "DB_USER": user,
        "DB_PASSWORD": password
    }

    missing_variables = [
        name
        for name, value in required_variables.items()
        if not value
    ]

    if missing_variables:
        raise ValueError(
            "Missing database environment variables: "
            + ", ".join(missing_variables)
        )

    return (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{database}"
    )


def get_engine():
    """
    Create and return a SQLAlchemy database engine.
    """

    database_url = get_database_url()

    return create_engine(database_url)


if __name__ == "__main__":

    engine = get_engine()

    try:
        with engine.connect() as connection:
            print("Database connection successful.")

    except Exception as error:
        print("Database connection failed.")
        print(error)