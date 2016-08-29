
from celery.utils.log import get_task_logger
from celery.task import task
from utils import download_documents

logger = get_task_logger(__name__)


@task
def task_download_documents(api_key, model):
    download_documents(api_key, model)
    logger.info("Downloaded all available documents")