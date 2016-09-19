from django.shortcuts import render, redirect, get_object_or_404

from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist, Q

from django.apps import apps

from django.conf import settings
from django.http import HttpResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required

from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
import urlparse

from django.core.mail import EmailMultiAlternatives
from django.core.files import File

from forms import *
from models import *

from hellosign_sdk import HSClient as HS

import sys
import os
import tempfile

# Create your views here.
# This is a modified version of the 'user_passes_test' decorator.
# It's a simple, hacky way to pass a request object to the test
# instead of request.user


def request_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the request object and returns True if the request passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                           settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, login_url, redirect_field_name)

        return _wrapped_view

    return decorator


def user_is_executive(request):
    if request.account_type == 'E':
        return True
    else:
        return False


def user_has_access(request):
    if request.user.account_type == 'E' or request.user.id == int(request.path.rsplit("/")[2]):
        return True
    else:
        return False


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
    if request.user.account_type == 'C':
        client = get_object_or_404(Client, user_id=request.user.id)
        client_form = ManageClientForm(instance=client)
        user_form = ManageUserForm(instance=request.user)
        pending = [document if getattr(client, '{}_status'.format(document)) == 'pending' else None
                          for document in ['nda', 'statement_of_work', 'consulting_agreement']]
        completed = [document if getattr(client, '{}_status'.format(document)) == 'completed' else None
                            for document in ['nda', 'statement_of_work', 'consulting_agreement']]
        forms = {
            'nda': NDAForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
            'statement_of_work': StatementOfWorkForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
            'consulting_agreement': ConsultingAgreementForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
            'purchase_request': PurchaseRequestForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
        }
        return render(request, 'partials/client-home.html',
                      {'client_form': client_form, 'user_form': user_form, 'client': client, 'pending': pending,
                       'completed': completed, 'forms': forms})
    return render(request, 'partials/home.html')


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def search(request, flag=None, query=None):
    if request.method == 'POST' or query:
        name = query or request.POST['search']
        if name == '':
            clients = AbstractUserModel.objects.filter(account_type='C')
        else:
            for term in name.split():
                clients = AbstractUserModel.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) |
                                                           Q(email__icontains=term),
                                                           account_type='C')
        client_list = [client.client for client in clients]
        if len(client_list) == 0:
            messages.warning(request, 'We couldn\'t find anything using the search term: "%s"! Try modifying your search!' % name)
        return render(request, 'partials/search-results.html', {'clients': client_list, 'query': name,
                                                                'flag': 'user.%s' % flag if flag else 'user.first_name'})
    else:
        clients = AbstractUserModel.objects.filter(account_type='C')
        client_list = [client.client for client in clients]
        if len(client_list) == 0:
            messages.error(request, "We couldn't find any clients in the database. "
                                    "Please contact the system administrator.")
        return render(request, 'partials/search-results.html', {'clients': client_list, 'query': query or 'browse',
                                                                'flag': 'user.%s' % flag if flag else 'user.first_name'})


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
    user = get_object_or_404(Client, user_id=user_id)
    return render(request, 'partials/client.html', {'client': user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def contact(request, user_id):
    user = get_object_or_404(Client, user_id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
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
            messages.success(request, "The client {}, has been emailed successfully.".format(user.user.get_full_name()))
            form = ContactForm()
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
        else:
            messages.error(request, 'Please correct the errors below!')
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
    else:
        form = ContactForm(initial={'to': user.user.email, 'cc': request.user.email})
        return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def remind_user(request, user_id, document_type):
    user = get_object_or_404(Client, user_id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
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
            messages.success(request, "The client {}, has been emailed successfully.".format(user.user.get_full_name()))
            form = ContactForm()
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
        else:
            messages.error(request, 'Please correct the errors below!')
            return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})
    else:
        form = ContactForm(initial={'to': user.email, 'cc': request.user.email,
                                    'subject': 'Hello, {}, please fill out this {} form.'.format(user.user.first_name,
                                                                                                 document_type.upper()),
                                    'message': 'Hi, our systems indicate that we\'ve sent you an NDA form to complete, '
                                               'but we have not received the signed document. Your Raise executive, {}, '
                                               'has requested to remind you to please fill out this form and sign the '
                                               'document. Thanks!'.format(request.user.get_full_name())})
        return render(request, 'partials/contact.html', {'form': form, 'client': user, 'user': request.user})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def onboard_forms(request, user_id, document_type):
    """
    We need to do a few things with this forms view. We need a generic view to handle creation of any given form,
    NDA, Statement of Work, Consulting Agreement, and Purchase Request. We need to allow the Executive to verify that
    the auto-generated information is correct and sign the document, then send the signed document to a Client. We also
    need to store the document in our database as well as an attachment in, say, SmartSheet or a Google Doc.
    :param request:
    :return: HTML object: generated form (integrated with HelloSign API), or gather information for that form.
    """
    client = get_object_or_404(Client, user_id=user_id)
    types = {
        'nda': NDAForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
        'statement_of_work': StatementOfWorkForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
        'consulting_agreement': ConsultingAgreementForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
        'purchase_request': PurchaseRequestForm(request.POST or None, initial={'email': client.user.email, 'name': client.user.get_full_name()}),
    }
    form = types.get(document_type, None)
    if form.is_valid():
        cd = form.cleaned_data
        custom_fields = [
            {'email': cd['email']},
            {"full_name": cd['name']},
            {"exec_title": request.user.executive.title if request.user.account_type == 'E' else client.executive.title},
            {"exec_name": request.user.get_full_name() if request.user.account_type == 'E' else client.executive.user.get_full_name()},
        ]
        if document_type == 'statement_of_work':
            if request.POST['milestone2']:
                custom_fields.append({'milestone': 'Project Commencement'})
                custom_fields.append({'milestone6': 'Project Completion'})
                for i in range(1, 7):
                    if request.POST['milestone{0}'.format(i)] and request.POST['milestone_desc{0}'.format(i) and
                                    request.POST['milestone_date{0}'.format(i)]]:
                        custom_fields.append({'milestone{0}'.format(i): request.POST['milestone{0}'.format(i)]})
                        custom_fields.append({'milestone_desc{0}'.format(i): request.POST['milestone_desc{0}'.format(i)]})
                        custom_fields.append({'milestone_date{0}'.format(i): request.POST['milestone_date{0}'.format(i)]})
            if request.POST['deliverables1']:
                for i in range(1, 6):
                    if request.POST['deliverables{0}'.format(i)] and request.POST['deliverables_desc{0}'.format(i) and
                            request.POST['deliverables_date{0}'.format(i)]]:
                        custom_fields.append({'deliverables{0}'.format(i): request.POST['deliverables{0}'.format(i)]})
                        custom_fields.append({'deliverables_desc{0}'.format(i): request.POST['deliverables_desc{0}'.format(i)]})
                        custom_fields.append({'deliverables_date{0}'.format(i): request.POST['deliverables_date{0}'.format(i)]})
            if request.POST['fees1']:
                for i in range(1, 6):
                    if request.POST['fees{0}'.format(i)] and request.POST['fees_date{0}'.format(i)]:
                        custom_fields.append({'fees{0}'.format(i): request.POST['fees{0}'.format(i)]})
                        custom_fields.append({'fees_date{0}'.format(i): request.POST['fees_date{0}'.format(i)]})

        stripped_type = document_type.replace('_', "")
        model = getattr(client, document_type) or apps.get_model(app_label='forms', model_name=stripped_type).objects.create(executive=client.executive)
        for field, value in cd.iteritems():
            if field not in ['email', 'name', 'ssn']:
                custom_fields.append({field:value})
                setattr(model, field, value)
        model.save()
        setattr(client, document_type, model)
        setattr(client, '{}_file'.format(document_type), None)
        client.save()
        signature_request = generic_template_handler(request, document_type, custom_fields)
        messages.success(request,
                         'The {} form has been mailed for signatures. You can check it\'s status at {}.'.format(document_type,
            signature_request.details_url))
        return redirect('/clients/{}/'.format(client.user_id))
    return render(request, 'partials/forms.html', {'form': form, 'status': getattr(client, '{}_status'.format(document_type)),
                   'document_type': document_type, 'client': client, 'document': getattr(client, '{}_file'.format(document_type))})


@login_required(login_url='/login/')
def tokenized_form_handler(request, user_id, document_type, token):
    client = get_object_or_404(Client, user_id=user_id)
    if client.generate_token(document_type) == token:
        return onboard_forms(request, user_id, document_type)
    else:
        return HttpResponseBadRequest("Error! Token is invalid!")


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def send_document(request, user_id, document_type):
    user = get_object_or_404(Client, user_id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
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
        doc_file.save('{}/{}/{}.pdf'.format(user.user.get_full_name(), document_type, getattr(user, '{}_id'.format(document_type))),
                      File(document), save=True)
        user.save()
        messages.success(request, 'We retrieved the document!')
    document.close()
    return redirect('/clients/{}/forms/{}/'.format(user_id, document_type))


@login_required(login_url='/login/')
@request_passes_test(user_has_access, login_url='/login/')
def manage(request, user_id):
    client = get_object_or_404(Client, user_id=user_id)
    client_form = ManageClientForm(request.POST or None, instance=client)
    user_form = ManageUserForm(request.POST or None, instance=client.user)
    if client_form.is_valid() and user_form.is_valid():
        client_form.save()
        user_form.save()
        messages.success(request, "You've succesfully updated the following fields: '%s'" % ', '.join(client_form.updated + user_form.updated))
    else:
        if request.method != 'GET':
            messages.error(request, 'Please correct the errors below')
    if request.user.account_type == 'E':
        return render(request, 'partials/manage.html', {'client_form': client_form, 'user_form': user_form, 'client': client})
    else:
        return render(request, 'partials/client-home.html', {'client_form': client_form, 'user_form': user_form, 'client': client})


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def deactivate(request, user_id):
    if request.method == 'POST':
        client = get_object_or_404(Client, user_id=user_id)
        client.user.is_active = False
        client.user.save()
        messages.success(request, "%s has been deactivated. You will not be able to see %s in any searches" %
                         (client.user.get_full_name(), client.user.first_name))
    return redirect('/clients/{}/manage'.format(user_id))


@login_required(login_url='/login/')
@user_passes_test(user_is_executive)
def reactivate(request, user_id):
    if request.method == 'POST':
        client = get_object_or_404(Client, user_id=user_id)
        client.user.is_active = True
        client.user.save()
        messages.success(request, "%s has been reactivate. You will now see them in searches and be able to generate "
                                  "forms for them." % client.user.get_full_name())
    return redirect('/clients/{}/manage'.format(user_id))


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
    try:
        signature_request = client.send_signature_request_with_template(
                                        test_mode=True,
                                        # client_id=settings.CLIENT_ID,
                                        template_id=settings.TEMPLATE_IDS.get(template_id.upper()),
                                        title="{0} form with Raise Inc.".format(template_id),
                                        subject="Please sign this {0} form".format(template_id),
                                        message="Please sign and verify all fields on this {0} form.".format(template_id),
                                        signing_redirect_url=None,
                                        signers=signers,
                                        custom_fields=custom_fields[1:]
        )
    except Exception:
        return None
    raise_client.client.active_request_id = signature_request.signature_request_id
    raise_client.client.save()
    return signature_request
