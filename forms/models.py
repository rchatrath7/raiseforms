from __future__ import unicode_literals
from django.db import models
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
import raiseforms.settings as settings
import sys, os
from datetime import datetime, timedelta

# Create your models here.


def file_upload_path(instance, filename):
    # Upload file to MEDIA_ROOT/user.id/filename
    # Perhaps adjust for renaming the files from something less ugly to something more readable - maybe the file ID
    # We could also remove all file handling to the individual classes
    return 'MEDIA_ROOT/documents/' + filename

# Abstract User and Manager models taken from https://thinkster.io/django-angularjs-tutorial


class AbstractUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):
        user = self.create_user(email, password, **kwargs)

        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        return user


class AbstractUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    account_types = (
        ('C', 'Client'),
        ('E', "Executive")
    )

    account_type = models.CharField(max_length=1, choices=account_types, default='E')

    is_admin = models.BooleanField(default=account_type == 'E', verbose_name='Admin')
    is_admin.help_text = "All Executives are considered Admins, but Clients are not."
    is_admin.disabled = True

    _is_active = models.BooleanField(default=account_type == 'E', verbose_name='Active')
    _is_active.help_text = "All Executives are active upon creation. Clients must fill out the register form before " \
                           "their account becomes activated."
    _is_active.disabled = True

    objects = AbstractUserManager()

    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return ' '.join([self.first_name, self.last_name])

    def get_short_name(self):
        return self.first_name

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @property
    def is_staff(self):
        return self.is_active

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Executive(models.Model):
    # Raise Executive
    title = models.CharField(max_length=30)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)


class NDA(models.Model):
    # TODO: Put in validators
    # NDA FORM
    ssn = models.CharField(max_length=11, null=True)
    location = models.CharField(max_length=100, null=True)
    corporation = models.CharField(max_length=100, null=True)
    title = models.CharField(max_length=20, null=True)
    agreement_date = models.DateTimeField(auto_now_add=True)

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<SSN: %s, Location: %s, Corporation: %s, Title: %s, Agreement Date: %s, Executive: %s>"\
            % (self.ssn, self.location, self.corporation, self.title, self.agreement_date, self.executive)

    class Meta:
        verbose_name = 'NDA'
        verbose_name_plural = 'NDA Forms'


class StatementOfWork(models.Model):
    # TODO: Put in validators; Need to figure out how to handle the id; can use the auto-incrementing id or use the id
    # of the user; Also need to figure out handling tables
    desc_of_services = models.TextField(null=True)
    # Not sure if we need this yet
    agreement_date = models.DateTimeField(auto_now_add=True, null=True)
    milestones = models.NullBooleanField()
    # Milestone tables
    deliverables = models.NullBooleanField()
    # Deliverables Table
    # We can probably use a much better way of determining which payment method is used, but for now will just have fields
    hourly_pricing = models.NullBooleanField()
    fixed_pricing = models.NullBooleanField()
    milestone_pricing = models.NullBooleanField()
    hourly_rate = models.FloatField(null=True)
    fixed_rate = models.FloatField(null=True)
    milestone_rate = models.FloatField(null=True)
    additional_terms_of_services = models.TextField(null=True)

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<Statement Of Work: %s, Executive: %s>" % (self.id, self.executive)

    class Meta:
        verbose_name = 'Statement of Work'
        verbose_name_plural = 'Statement of Work Forms'


class ConsultingAgreement(models.Model):
    agreement_date = models.DateTimeField(auto_now_add=True)

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<Consulting Agreement: %s, Agreement Date: %s, Executive: %s>"\
               % (self.id, self.agreement_date, self.executive)

    class Meta:
        verbose_name = 'Consulting Agreement'
        verbose_name_plural = 'Consulting Agreement Forms'


class PurchaseRequest(models.Model):
    # TODO: I'd like to add properties and in general cleaner ways of handling things
    date = models.DateTimeField(auto_now_add=True)
    cost_center = models.CharField(max_length=50, null=True)
    # Client/Owner
    # requester = models.ForeignKey(Client)
    executive= models.ForeignKey(Executive)
    vendor = models.CharField(max_length=30, null=True)
    description = models.TextField(null=True)
    purpose = models.TextField(null=True)
    amount = models.FloatField(null=True)
    # This should be a date range, just adjust it to get the difference in time
    service_period = models.DateTimeField(null=True)
    # Handle 'either-ors' better (invoice, payment_type, etc)
    contract_present = models.NullBooleanField()
    invoice_cadence_recurring = models.NullBooleanField(default=False)
    recurring_date = models.DateTimeField(null=True)
    choices = (
        ('ach', 'ACH'),
        ('credit', 'Credit'),
        ('check', 'Check'),
        ('abacus', 'Abacus')
    )
    payment_type = models.CharField(choices=choices, max_length=6)
    payment_types = {
        'ach': models.NullBooleanField(default=False),
        'credit': models.NullBooleanField(default=False),
        'check': models.NullBooleanField(default=False),
        'abacus': models.NullBooleanField(default=False)
    }
    payment_terms_net_30 = models.NullBooleanField(default=False)
    payment_terms_receipt = models.NullBooleanField(default=False)

    additional_notes = models.TextField(null=True)

    def __str__(self):
        return "<Purchase Request: %s, Date: %s, Cost Center: %s, Requester: %s, Owner: %s, Payment Type: %s>"\
            % (self.id, self.date, self.cost_center, self.requester, self.owner, self.payment_type)

    class Meta:
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Request Forms'


class Client(models.Model):
    # The client is the person signing. We want to be able to send them multiple forms if possible, as well as gather
    # All necessary information at once.
    # TODO: Figure out file uploading/googledocs support.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True)
    address = models.CharField(max_length=100, null=True)
    token = models.CharField(max_length=16, null=True)
    active_request_id = models.CharField(max_length=200, null=True)

    nda_token = models.CharField(max_length=16, null=True)
    nda = models.ForeignKey(NDA, null=True)
    nda_file = models.FileField(upload_to=file_upload_path, null=True)

    statement_of_work_token = models.CharField(max_length=16, null=True)
    statement_of_work = models.ForeignKey(StatementOfWork, null=True)
    statement_of_work_file = models.FileField(upload_to=file_upload_path, null=True)

    consulting_agreement_token = models.CharField(max_length=16, null=True)
    consulting_agreement = models.ForeignKey(ConsultingAgreement, null=True)
    consulting_agreement_file = models.FileField(upload_to=file_upload_path, null=True)

    purchase_request_file = models.FileField(upload_to=file_upload_path, null=True)

    # Relations
    executive = models.ForeignKey(Executive, null=True)

    # Purchase Request ForeignKey

    # Properties
    @property
    def nda_status(self):
        if self.nda and self.nda_file:
            return "completed"
        elif self.nda and not self.nda_file:
            return "pending"
        else:
            return "incomplete"

    @property
    def statement_of_work_status(self):
        if self.statement_of_work and self.statement_of_work_file:
            return "completed"
        elif self.statement_of_work and not self.statement_of_work_file:
            return "pending"
        else:
            return "incomplete"

    @property
    def expired(self):
        return datetime.utcnow() + timedelta(2)

    @property
    def is_redeemable(self):
        return self.expired < datetime.utcnow() and not self.is_active

    @property
    def consulting_agreement_status(self):
        if self.consulting_agreement and self.consulting_agreement_file:
            return "completed"
        elif self.consulting_agreement and not self.consulting_agreement_file:
            return "pending"
        else:
            return "incomplete"

    def generate_token(self, document_type):
        token = getattr(self, '{}_token'.format(document_type))
        if token:
            return token
        else:
            new_token = os.urandom(8).encode('hex')
            setattr(self, '{}_token'.format(document_type), new_token)
            self.save()
            return new_token
        # if document_type == 'nda':
        #     if not self.nda_token:
        #         self.nda_token = os.urandom(8).encode('hex')
        # elif document_type == 'statement_of_work':
        #     if not self.statement_of_work_token:
        #         self.statement_of_work_token = os.urandom(8).encode('hex')
        # elif document_type == 'consulting_agreement':
        #     consulting_agreement_token = os.urandom(8).encode('hex')
        # else:
        #     return HttpResponseBadRequest("Error! Document type not found, acceptable document types include: 'NDA', "
        #                                   "'Statement of Work', and 'Consulting Agreement'.")


@receiver(post_save, sender=AbstractUserModel)
def abstract_user_creation(sender, instance, created, **kwargs):
    if created:
        if instance.account_type == 'C':
            Client.objects.create(user=instance)
        else:
            Executive.objects.create(user=instance)
