from django.core.files import File
from hellosign_sdk import HSClient as HS
from celery.utils.log import get_task_logger
import tempfile
from django.apps import apps


logger = get_task_logger(__name__)


def download_documents(api_key):
    model = apps.get_model(app_label='forms', model_name='AbstractUserModel')
    logger.info("Starting retrieval")
    hsClient = HS(api_key=api_key)
    clients = [client.client if client.is_active else None for client in model.objects.filter(
        account_type='C'
    )]
    logger.info("Got clients: <%s>" % clients)
    document_types = ['nda', 'statement_of_work', 'consulting_agreement']
    document_type = None
    for client in clients:
        if client and client.active_request_id:
            for _type in document_types:
                if getattr(client, '{}_status'.format(_type)) == 'pending':
                    document_type = _type
            if document_type:
                request = hsClient.get_signature_request(client.active_request_id)
                logger.info("Gathered signature request: %s" % request)
                if request.is_complete:
                    document = tempfile.TemporaryFile()
                    status = hsClient.get_signature_request_file(
                        signature_request_id=str(client.active_request_id),
                        path_or_file=document,
                        file_type='pdf'
                    )
                    if status:
                        logger.info("Successfully downloaded document: %s" % document)
                        doc_file = getattr(client, '{}_file'.format(document_type))
                        doc_file.save('{}/{}/{}'.format(client.user.get_full_name(), document_type,
                                                        getattr(client, '{}_id'.format(document_type))),
                                      File(document), save=True)
                        client.active_request_id = None
                        client.save()
                    else:
                        logger.error("Error downloading document: <%s, %s>" % (document, status))
                    document.close()
                    logger.info("Closed document.")