from django.conf import settings
import requests


def send_mail(recipients, subject, message, request, from_name='', reply_to=''):
    if isinstance(recipients, list):
        recipients = recipients
    else:
        recipients = [recipients]
    if from_name:
        sender = "%s <%s>" % (from_name, settings.MAILGUN_EMAIL_ADDRESS)
    else:
        sender = "Raise Forms Mailer <%s>" % settings.MAILGUN_EMAIL_ADDRESS
    try:
        return requests.post(
            settings.MAILGUN_BASE_URL,
            auth=("api", settings.MAILGUN_API_KEY),
            data={"from": sender,
                  "to": recipients,
                  "subject": subject,
                  "text": message})

    except Exception, e:
        raise e