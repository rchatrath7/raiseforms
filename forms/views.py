from django.shortcuts import render, redirect, get_object_or_404

from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist, Q

from django.conf import settings

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required

from django.core.mail import EmailMultiAlternatives
from django.core.files import File

from forms import *
from models import *

from hellosign_sdk import HSClient as HS

import sys
import os
import tempfile

# Create your views here.
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
                messages.error(request, 'Invalid User! This user has an inactive account, please renew their account.')
                return render(request, 'partials/login.html')
        else:
            messages.error(request, 'Invalid credentials! Either your username or password were not valid.')
            return render(request, 'partials/login.html')
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
        name = request.POST['search']
        if name == '':
            clients = AbstractUserModel.objects.filter(account_type='C', _is_active=True)
        else:
            for term in name.split():
                clients = AbstractUserModel.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) |
                                                           Q(email__icontains=term),
                                                           account_type='C')
        if len(list(clients)) == 0:
            messages.warning(request, 'We couldn\'t find anything using the search term: "%s"! Try modifying your search!' % name)
        return render(request, 'partials/search-results.html', {'clients': list(clients), 'query': name})
    else:
        clients = AbstractUserModel.objects.filter(account_type='C', _is_active=True)
        if len(list(clients)) == 0:
            messages.error(request, "We couldn't find any clients in the database. "
                                    "Please contact the system administrator.")
        return render(request, 'partials/search-results.html', {'clients': list(clients), 'query': 'browse'})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def invite_client(request):
    if request.method == 'POST':
        email = request.POST['email']
        token = os.urandom(8).encode('hex')
        try:
            tokenized_user = AbstractUserModel(email=email, account_type='C')
            tokenized_user.set_unusable_password()
            tokenized_user.save()
            tokenized_user.client.executive_id, tokenized_user.client.token = request.user.executive.id, token
            tokenized_user.client.save()
            auth_url = request.META['HTTP_HOST'] + '/accounts/register/' + token
            msg = EmailMultiAlternatives(
                subject="Please register your Raise-Forms client account!",
                body="You have been invited to create a raise-forms account. Please click %s " \
                     "and fill out all fields so that you can begin the on-boarding process at " \
                     "Raise. Thanks! Note: this URL wil expire in exactly two days from now." % auth_url,
                to=[email, request.user.email])
            msg.send()
            messages.success(request, 'The client has been emailed a link to register with raise-forms.')
            return render(request, 'partials/invite-client.html')
        except IntegrityError:
            messages.error(request, 'This client already exists! Please add a new client.')
            return render(request, 'partials/invite-client.html')
        except Exception:
            messages.error(request, 'An unknown error occurred! Please contact the system administrator.')
            return render(request, 'partials/invite-client.html')
    else:
        return render(request, 'partials/invite-client.html')


# @user_passes_test()
def register(request, auth_token):
    token = get_object_or_404(Client, token=auth_token)
    is_expired = datetime.utcnow() >= token.expired
    if not is_expired and not token.user.is_active:
        if request.method == 'POST':
            form = ClientForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                # temporary solution
                token.user.first_name = cd['first_name']
                token.user.last_name = cd['last_name']
                token.user.email = cd['email']
                token.address = cd['address']
                token.user.set_password(cd['password'])
                token.user.is_active = True
                token.user.save()
                token.save()
            else:
                return render(request, 'partials/register-form.html', {'form': form})
            messages.success(request, "You have successfully registered with raise-forms! Please wait for your "
                                      "Raise executive to send you the required forms.")
            return redirect('/')
        else:
            form = ClientForm(initial={'email': token.user.email})
            return render(request, 'partials/register-form.html', {'form': form})
    else:
        messages.error(request, "Sorry, this URL has expired. Please contact your Raise executive to invite you.")
        return redirect('/')
    # except DoesNotExist e:
    #     messages.error(request, "Sorry, this URL is not valid. Please wait for your Raise executive to send you "
    #                             "a valid invitation.")
    #     return redirect('/')


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def client_panel(request, user_id):
    """
    This handles the commands for interfacing with a specific user. If we don't have the basic information of the user,
    then the only option available should be to send a user the form to gather essential information. However, if the
    information is already present, then that should be displayed and we want to give the Executive admin controls as
    well as capability to generate (and gather the necessary information for) the designated on-boarding form.
    :param request:
    :return: HTML object: user interface.
    """
    user = get_object_or_404(AbstractUserModel, id=user_id)
    return render(request, 'partials/client.html', {'client': user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def contact(request, user_id):
    user = get_object_or_404(AbstractUserModel, id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
            to = cd['to']
            cc = cd['cc']
            sender = request.user.get_full_name() + "<admin@raiseforms.com>"
            subject = cd['subject']
            message = cd['message']
            msg = EmailMultiAlternatives(
                to=[to],
                cc=[cc],
                from_email=sender,
                subject=subject,
                body=message
            )
            msg.send()
            messages.success(request, "The client {}, has been emailed successfully.".format(user.get_full_name))
            form = ContactForm()
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
        else:
            messages.error(request, 'Please correct the errors below!')
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
    else:
        form = ContactForm(initial={'to': user.email, 'cc': request.user.email})
        return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def remind_user(request, user_id, document_type):
    user = get_object_or_404(AbstractUserModel, id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
            to = cd['to']
            cc = cd['cc']
            sender = request.user.get_full_name() + "<admin@raiseforms.com>"
            subject = cd['subject']
            message = cd['message']
            msg = EmailMultiAlternatives(
                to=[to],
                cc=[cc],
                from_email=sender,
                subject=subject,
                body=message
            )
            msg.send()
            messages.success(request, "The client {}, has been emailed successfully.".format(user.get_full_name))
            form = ContactForm()
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
        else:
            messages.error(request, 'Please correct the errors below!')
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
    else:
        form = ContactForm(initial={'to': user.email, 'cc': request.user.email,
                                    'subject': 'Hello, {}, please fill out this {} form.'.format(user.first_name,
                                                                                                 document_type.upper()),
                                    'message': 'Hi, our systems indicate that we\'ve sent you an NDA form to complete, '
                                               'but we have not received the signed document. Your Raise executive, {}, '
                                               'has requested to remind you to please fill out this form and sign the '
                                               'document. Thanks!'.format(request.user.get_full_name())})
        return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})


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
@user_passes_test(user_is_executive)
def nda(request, user_id):
    client = get_object_or_404(Client, user_id=user_id)
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
                {"exec_title": request.user.executive.title if request.user.account_type == 'E' else client.executive.title},
                {"exec_name": request.user.get_full_name() if request.user.account_type == 'E' else client.executive.user.get_full_name()}
            ]
            if request.user.account_type == 'E':
                # create NDA relationship with client
                if not client.nda:
                    nda = NDA(
                        ssn=cd['ssn'],
                        location=cd['location'],
                        corporation=cd['corporation'],
                        title=cd['title'],
                        executive=request.user.executive
                    )
                    nda.save()
                    client.nda = nda
                else:
                    for field, value in cd.iteritems():
                        if field not in ['email', 'full_name']:
                            setattr(client.nda, field, value)
                    client.nda.save()
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
                client.nda = NDA.objects.get(id=nda.id)
                client.save()
            signature_request = generic_template_handler(request, "NDA", custom_fields)
            messages.success(request,
                             'The NDA form has been mailed for signatures. You can check it\'s status at {}.'.format(
                signature_request.details_url))
            return render(request, 'partials/nda_form.html', {'nda_form': form})
        else:
            return render(request, 'partials/nda_form.html', {'form': form, 'status': client.nda_status,
                                                              'document_type': 'nda', 'client': client})
    else:
        form = NDAForm()
        return render(request, 'partials/nda_form.html', {'form': form, 'status': client.nda_status,
                       'document_type': 'nda', 'client': client})


@login_required(login_url='/login/')
def statement_of_work(request, client_id):
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
                client = AbstractUserModel.objects.get(id=user_id).client
                client.nda = nda
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
            signature_request = generic_template_handler(request, "NDA", custom_fields)
            messages.success(request, 'The NDA form has been mailed for signatures. You can check it\'s status at {}.').format(signature_request.details_url)
            return render(request, 'partials/nda_form.html', {'nda_form': form})
        else:
            return render(request, 'partials/nda_form.html', {'nda_form': form})
    else:
        form = NDAForm()
        return render(request, 'partials/nda_form.html', {'nda_form': form})

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
@user_passes_test(user_is_executive)
def send_document(request, user_id, document_type):
    user = get_object_or_404(AbstractUserModel, id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid:
            cd = form.cleaned_data
            to = cd['to']
            cc = cd['cc']
            sender = request.user.get_full_name() + "<admin@raiseforms.com>"
            subject = cd['subject']
            message = cd['message']
            msg = EmailMultiAlternatives(
                to=[to],
                cc=[cc],
                from_email=sender,
                subject=subject,
                body=message
            )
            msg.send()
            messages.success(request, "The client {}, has been emailed successfully.".format(user.get_full_name))
            form = ContactForm()
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
        else:
            messages.error(request, 'Please correct the errors below!')
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
    else:
        token = user.client.generate_token(document_type)
        auth_url = request.META['HTTP_HOST'] + '/clients/' + user_id + '/forms/' + document_type + '/' + token
        form = ContactForm(initial={'to': user.email, 'cc': request.user.email,
                                    'subject': 'Hello, {}, please fill out this {} form.'.format(user.get_full_name(), document_type.upper()),
                                    'message': 'Hi, our systems indicate that we\'ve sent you an NDA form to complete, '
                                               'but we have not received the sign document. Your Raise executive, {}, '
                                               'has requested to remind you to please fill out this form and sign the '
                                               'document {}. Thanks!'.format(request.user.get_full_name(), auth_url)})
        return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def retrieve(request, user_id, document_type):
    client = HS(api_key=settings.HELLOSIGN_API_KEY)
    user = get_object_or_404(Client, user_id=user_id)
    document = tempfile.TemporaryFile()
    status = client.get_signature_request_file(
        signature_request_id=str(user.active_request_id),
        path_or_file=document,
        file_type='pdf'
    )
    if not status:
        messages.warning(request, 'The file is still being prepared. Please wait for the document to be completed.')
    else:
        doc_file = getattr(user, '{}_file'.format(document_type))
        doc_file.save('{}/{}/{}'.format(user.user.get_full_name(), document_type, getattr(user, '{}_id'.format(document_type))),
                      File(document), save=True)
        user.save()
        messages.success(request, 'We retrieved the document!')
    document.close()
    return redirect('/clients/{}/forms/{}/'.format(user_id, document_type))


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
        {'role_name': 'Executive', 'name': request.user.get_full_name() if request.user.account_type == 'E' else
            request.user.executive.user.get_full_name(), 'email_address': request.user.email},
        {'role_name': 'Client', 'name': custom_fields[1]['full_name'], "email_address": custom_fields[0]['email']}
    ]
    raise_client = get_object_or_404(AbstractUserModel, email=custom_fields[0]['email'])
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
    raise_client.client.active_request_id = signature_request.signature_request_id
    raise_client.client.save()
    return signature_request
    # DO something with this signature request - return response?
    # for signature in signature_request.signatures:
    #     embedded_obj = client.get_embedded_object(signature.signature_id)
    #     sign_url = embedded_obj.sign_url
    #     return sign_url

    # return ""
