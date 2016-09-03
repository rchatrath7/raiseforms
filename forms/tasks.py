from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery.task import task
from forms.form_utils import download_documents

logger = get_task_logger(__name__)


@task(name="task-download-documents")
def task_download_documents(api_key):
    download_documents(api_key)
    logger.info("Downloaded all available documents")