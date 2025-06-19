from src.data.cleaner import parse_and_clean_pdfs
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_data():
    logger.info("CLEANING DOCUMENTS")
    parse_and_clean_pdfs()
    logger.info("DOCUMENTS CLEANED SUCCESSFULLY")


if __name__ == "__main__":
    clean_data()
