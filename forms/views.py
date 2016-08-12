from django.shortcuts import render, redirect

from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required

from django.core.mail import EmailMultiAlternatives

from forms import *
from models import *

from hellosign_sdk import HSClient as HS

import sys

# Create your views here.
# TODO: Compartmentalize the forms view to handle one thing at a time.
# TODO: Add an "all-purpose" form view


def user_is_executive(request):
    if request.account_type == 'E':
        return True
    else:
        return False


# def user_has_token(request, token):
#     if request.user.

def login_handler(request):
    if request.method == 'POST':
        username = request.POST['username'].encode('utf-8')
        password = request.POST['password'].encode('utf-8')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(request.GET['next'])
            else:
                pass
                # Raise inactive user error
        else:
            pass
            # Raise invalid login message.
    else:
        return render(request, 'partials/login.html')


def logout_handler(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/login/')
def home(request):
    """
    This handles the homepage view-it should return a log in page if the user hasn't authenticate, or, the main page
    view which gives the user the option to search for a group of users and admin controls.
    :param request:
    :return: HTML object, either a login page, or a the main page.
    """
    return render(request, 'partials/home.html')


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def search(request):
    if request.method == 'POST':
        email = request.POST['email']
        emails = Client.user.objects.values_list('email', flat=True)
        if email in emails:
            return render(request, 'partials/search-results.html', {'emails': emails})
        else:
            return render(request, 'partials/search-results.html', {'emails': []})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def invite_client(request):
    if request.method == 'POST':
        email = request.POST['email']
        tokenized_user = AbstractUserModel(email=email, account_type='C')
        tokenized_user.set_unusable_password()
        #tokenized_user.save()
        auth_token = tokenized_user.invitation
        auth_url = request.get_host() + 'accounts/register/' + auth_token
        msg = EmailMultiAlternatives(
            subject="Please register your Raise-Forms client account!",
            body="You have been invited to create a raise-forms account by %s. Please click %s " \
                 "and fill out all fields so that you can begin the on-boarding process at " \
                 "Raise. Thanks!" % (tokenized_user.expired, auth_url),
            to=[email, request.user.email])
        print >> sys.stderr, msg
        msg.send()
        return redirect('/')
        # Render success to success page
        # redirect()
    else:
        return render(request, 'partials/invite-client.html')


# @user_passes_test()
def register(request, auth_token):
    if auth_token:
        token = AbstractUserModel.objects.get('invitation' == auth_token)
        if not token.expired and not token.is_active:
            if request.method == 'POST':
                form = ClientForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    # temporary solution
                    token.first_name = cd['first_name']
                    token.last_name = cd['last_name']
                    token.email = cd['email']
                    token.client.address = cd['address']
                    token.set_password(cd['password'])
                    token.save()
                else:
                    return render(request, 'partials/register-form.html', {'form': form})
                return render(request, 'partials/success-page.html')
            else:
                form = ClientForm(initial={'email': token.email})
                return render(request, 'partials/register-form.html', {'form': form})
        else:
            return render('request', 'partials/login.html')


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
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


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def nda(request, user_id):
    if request.method == 'POST':
        form = NDAForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            custom_fields = [
                {'email': cd['email']},
                {"full_name": cd['name']},
                {"corporation": cd['corporation']},
                {"location": cd['location']},
                {"title": cd['title']},
                {"exec_title": request.user.executive.title},
                {"exec_name": request.user.get_full_name()}
            ]
            if request.user.account_type == 'E':
                # create NDA relationship with client
                nda = NDA(
                    ssn=cd['ssn'],
                    location=cd['location'],
                    corporation=cd['corporation'],
                    title=cd['title'],
                    executive=request.user.executive
                )
                nda.save()
                client = Client.objects.get(id=user_id)
                client.nda = NDA.objects.get(id=nda.id)
                client.save()
            elif request.user.account_type == 'C':
                # save
                nda = NDA(
                    ssn=cd['ssn'],
                    location=cd['location'],
                    corporation=cd['corporation'],
                    title=cd['title'],
                    executive=request.user.client.executive
                )
                nda.save()
                request.user.client.nda = NDA.objects.get(id=nda.id)
                request.user.client.save()
            generic_template_handler(request, "NDA", custom_fields)
            return render(request, 'partials/nda_form.html', {'embed_url': ""})
        else:
            return render(request, 'partials/nda_form.html', {'nda_form': form})
    else:
        form = NDAForm()
    return render(request, 'partials/nda_form.html', {'nda_form': form})


@login_required(login_url='/login/')
def statement_of_work(request):
    if request.method == 'POST':
        form = StatementOfWorkForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
    else:
        form = StatementOfWorkForm()
    return render(request, 'partials/user_form.html', {'form': form})


@login_required(login_url='/login/')
def purchase_request(request):
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
    else:
        form = PurchaseRequestForm()
    return render(request, 'partials/user_form.html', {'form': form})


@login_required(login_url='/login/')
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
        {'role_name': 'Executive', 'name': request.user.get_full_name(), 'email_address': request.user.email},
        {'role_name': 'Client', 'name': custom_fields[1]['full_name'], "email_address": custom_fields[0]['email']}
    ]
    signature_request = client.send_signature_request_with_template(
                                    test_mode=True,
                                    # client_id=settings.CLIENT_ID,
                                    template_id=settings.TEMPLATE_IDS.get(template_id),
                                    title="{0} form with Raise Inc.".format(template_id),
                                    subject="Please sign this {0} form".format(template_id),
                                    message="Please sign and verify all fields on this {0} form.".format(template_id),
                                    signing_redirect_url=None,
                                    signers=signers,
                                    custom_fields=custom_fields[1:]
    )
    # DO something with this signature request - return response?
    # for signature in signature_request.signatures:
    #     embedded_obj = client.get_embedded_object(signature.signature_id)
    #     sign_url = embedded_obj.sign_url
    #     return sign_url

    # return ""
