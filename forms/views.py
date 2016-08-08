from django.shortcuts import render
from django.conf import settings
import logging
import sys
from models import Executive, Client, NDA, StatementOfWork, ConsultingAgreement, PurchaseRequest
from forms import *
from hellosign_sdk import HSClient as HS

# Create your views here.
# TODO: Compartmentalize the forms view to handle one thing at a time.
# TODO: Add an "all-purpose" form view

logger = logging.getLogger(__name__)

def home(request):
    """
    This handles the homepage view-it should return a log in page if the user hasn't authenticate, or, the main page
    view which gives the user the option to search for a group of users and admin controls.
    :param request:
    :return: HTML object, either a login page, or a the main page.
    """
    form = LoginForm()
    return render(request, 'partials/home.html', {'form': form})


def client_panel(request):
    """
    This handles the commands for interfacing with a specific user. If we don't have the basic information of the user,
    then the only option available should be to send a user the form to gather essential information. However, if the
    information is already present, then that should be displayed and we want to give the Executive admin controls as
    well as capability to generate (and gather the necessary information for) the designated on-boarding form.
    :param request:
    :return: HTML object: user interface.
    """
    pass


def forms(request):
    """
    We need to do a few things with this forms view. We need a generic view to handle creation of any given form,
    NDA, Statement of Work, Consulting Agreement, and Purchase Request. We need to allow the Executive to verify that
    the auto-generated information is correct and sign the document, then send the signed document to a Client. We also
    need to store the document in our database as well as an attachment in, say, SmartSheet or a Google Doc.
    :param request:
    :return: HTML object: generated form (integrated with Docusign API), or gather information for that form.
    """
    pass


def nda(request):
    if request.method == 'POST':
        form = NDAForm(request.POST)
        if form.is_valid():
            print >> sys.stderr, "Form is valid"
            cd = form.cleaned_data
            custom_fields = [
                {"full_name": "Raise Dev"},
                {"corporation": cd['corporation']},
                {"location": cd['location']},
                {"title": cd['title']},
                {"exec_title": "Dictator"},
                {"exec_name": "Raise Dev"}
            ]
            embed_url = generic_template_handler(request, "NDA", custom_fields)
            return render(request, 'partials/nda_document.html', {'embed_url': embed_url})
        else:
            print >> sys.stderr, "Form is not valid <{0}>".format(form.errors)
            return render(request, 'partials/nda_document.html')
    else:
        print >> sys.stderr, "Rendering input form"
        form = NDAForm()
    return render(request, 'partials/nda_form.html', {'nda_form': form})


def statement_of_work(request):
    if request.method == 'POST':
        form = StatementOfWorkForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
    else:
        form = StatementOfWorkForm()
    return render(request, 'partials/user_form.html', {'form': form})


def purchase_request(request):
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
    else:
        form = PurchaseRequestForm()
    return render(request, 'partials/user_form.html', {'form': form})


def manage(request):
    pass


def generic_template_handler(request, template_id, custom_fields):
    '''
    Take in a request, template type (NDA, Consulting Agreement, Fields, etc.) and get the hellosign template. This will
    be passed to our form processor for more logic to be done. This should be able to handle any type of form and return
    any form embeddable.
    :param request:
    :param template_id: The template type to be referenced (NDA, Consulting Agreement, Purchase Request, etc.)
    :param custom_fields: These are special fields unique to the template.
    :return: embeddable URL for an iFrame.
    '''
    client = HS(api_key=settings.HELLOSIGN_API_KEY)
    signers = [
        {'role_name': 'Executive', 'name': "Raise Dev", 'email_address': "raisedev1@gmail.com"},
        {'role_name': 'Client', 'name': "Rakesh", "email_address": 'rchatrath7@gmail.com'}
    ]
    signature_request = client.send_signature_request_embedded_with_template(
                                    test_mode=True,
                                    client_id=settings.CLIENT_ID,
                                    template_id=settings.TEMPLATE_IDS.get(template_id),
                                    title="{0} form with Raise Inc.".format(template_id),
                                    subject="Please sign this {0} form".format(template_id),
                                    message="Please sign and verify all fields on this {0} form.".format(template_id),
                                    signing_redirect_url=None,
                                    signers=signers,
                                    custom_fields=custom_fields
    )
    for signature in signature_request.signatures:
        embedded_obj = client.get_embedded_object(signature.signature_id)
        sign_url = embedded_obj.sign_url
        return sign_url

    return ""
