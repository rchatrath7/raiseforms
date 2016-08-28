from django.core.files import File
from models import AbstractUserModel
from hellosign_sdk import HSClient as HS
import tempfile


def download_documents(api_key):
    hsClient = HS(api_key=api_key)
    clients = [client.client if client.is_active else None for client in AbstractUserModel.objects.filter(
        account_type='C'
    )]
    document_types = ['nda', 'statement_of_work', 'consulting_agreement']
    for client in clients:
        if client and client.active_request_id:
            for _type in document_types:
                if getattr(client, '{}_status'.format(_type)) == 'pending':
                    document_type = _type
            request = hsClient.get_signature_request(client.active_request_id)
            if request.is_complete:
                document = tempfile.TemporaryFile()
                status = client.get_signature_request_file(
                    signature_request_id=str(client.active_request_id),
                    path_or_file=document,
                    file_type='pdf'
                )
                if status:
                    doc_file = getattr(client, '{}_file'.format(document_type))
                    doc_file.save('{}/{}/{}'.format(client.user.get_full_name(), document_type,
                                                    getattr(client, '{}_id'.format(document_type))),
                                  File(document), save=True)
                    client.active_request_id = None
                    client.save()
                document.close()