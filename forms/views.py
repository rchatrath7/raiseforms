from django.shortcuts import render
from models import Executive, Client, NDA, StatementOfWork, ConsultingAgreement, PurchaseRequest
from forms import *

# Create your views here.
# TODO: Compartmentalize the forms view to handle one thing at a time.
# TODO: Add an "all-purpose" form view


def home(request):
    """
    This handles the homepage view-it should return a log in page if the user hasn't authenticate, or, the main page
    view which gives the user the option to search for a group of users and admin controls.
    :param request:
    :return: HTML object, either a login page, or a the main page.
    """
    form = LoginForm()
    return render(request, 'partials/index.html', {'form': form})


def users(request):
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
        if form.is_valid:
            cd = form.cleaned_data
    else:
        form = NDAForm()
    return render(request, 'partials/user_form.html', {'form': form})


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
