
from celery.utils.log import get_task_logger

from forms.utils import download_documents

logger = get_task_logger(__name__)


def task_download_documents():
    download_documents()
    logger.info("Downloaded all available documents")