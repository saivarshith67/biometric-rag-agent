from .config import GOOGLE_API_KEY, DB_URL


def project_setup() -> None:
    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Please set it in your environment variables."
        )

    if not DB_URL:
        raise ValueError(
            "DB_URL is not set. Please set it in your environment variables."
        )
