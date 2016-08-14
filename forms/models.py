from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
import raiseforms.settings as settings
import sys
from datetime import datetime, timedelta

# Create your models here.


def file_upload_path(instance, filename):
    # Upload file to MEDIA_ROOT/user.id/filename
    # Perhaps adjust for renaming the files from something less ugly to something more readable - maybe the file ID
    # We could also remove all file handling to the individual classes
    return str(self.id) + '/' + filename

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

    token = models.CharField(max_length=16, null=True)

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
        return self.account_type == 'E'

    @property
    def is_staff(self):
        return self.is_active

    @property
    def expired(self):
        return datetime.utcnow() + timedelta(2)

    @property
    def is_redeemable(self):
        return self.expired < datetime.utcnow() and not self.is_active

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
    ssn = models.CharField(max_length=9)
    location = models.CharField(max_length=100)
    corporation = models.CharField(max_length=100)
    title = models.CharField(max_length=20)
    agreement_date = models.DateTimeField(auto_now_add=True)

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<SSN: %s, Location: %s, Corporation: %s, Title: %s, Agreement Date: %s, Client: %s, Executive: %s>"\
            % (self.ssn, self.location, self.corporation, self.title, self.agreement_date, self.client, self.executive)

    class Meta:
        verbose_name = 'NDA'
        verbose_name_plural = 'NDA Forms'


class StatementOfWork(models.Model):
    # TODO: Put in validators; Need to figure out how to handle the id; can use the auto-incrementing id or use the id
    # of the user; Also need to figure out handling tables
    desc_of_services = models.TextField()
    # Not sure if we need this yet
    agreement_date = models.DateTimeField(auto_now_add=True)
    milestones = models.BooleanField()
    # Milestone tables
    deliverables = models.BooleanField()
    # Deliverables Table
    # We can probably use a much better way of determining which payment method is used, but for now will just have fields
    hourly_pricing = models.BooleanField()
    fixed_pricing = models.BooleanField()
    milestone_pricing = models.BooleanField()
    hourly_rate = models.FloatField()
    fixed_rate = models.FloatField()
    milestone_rate = models.FloatField()
    additional_terms_of_services = models.TextField()

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<Statement Of Work: %s, Client: %s, Executive: %s>" % (self.id, self.client, self.executive)

    class Meta:
        verbose_name = 'Statement of Work'
        verbose_name_plural = 'Statement of Work Forms'


class ConsultingAgreement(models.Model):
    agreement_date = models.DateTimeField(auto_now_add=True)

    # Relations
    executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<Consulting Agreement: %s, Agreement Date: %s, Client: %s, Executive: %s>"\
               % (self.id, self.agreement_date, self.client, self.executive)

    class Meta:
        verbose_name = 'Consulting Agreement'
        verbose_name_plural = 'Consulting Agreement Forms'


class PurchaseRequest(models.Model):
    # TODO: I'd like to add properties and in general cleaner ways of handling things
    date = models.DateTimeField(auto_now_add=True)
    cost_center = models.CharField(max_length=50)
    # Client/Owner
    # requester = models.ForeignKey(Client)
    owner = models.ForeignKey(Executive)
    vendor = models.CharField(max_length=30)
    description = models.TextField()
    purpose = models.TextField()
    amount = models.FloatField()
    # This should be a date range, just adjust it to get the difference in time
    service_period = models.DateTimeField()
    # Handle 'either-ors' better (invoice, payment_type, etc)
    contract_present = models.BooleanField(default=False)
    invoice_cadence_recurring = models.BooleanField(default=False)
    recurring_date = models.DateTimeField()
    choices = (
        ('ach', 'ACH'),
        ('credit', 'Credit'),
        ('check', 'Check'),
        ('abacus', 'Abacus')
    )
    payment_type = models.CharField(choices=choices, max_length=6)
    payment_types = {
        'ach': models.BooleanField(default=False),
        'credit': models.BooleanField(default=False),
        'check': models.BooleanField(default=False),
        'abacus': models.BooleanField(default=False)
    }
    payment_terms_net_30 = models.BooleanField(default=False)
    payment_terms_receipt = models.BooleanField(default=False)

    additional_notes = models.TextField()

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
    nda_file = models.FileField(upload_to=file_upload_path, null=True)
    statement_of_work_file = models.FileField(upload_to=file_upload_path, null=True)
    consulting_agreement_file = models.FileField(upload_to=file_upload_path, null=True)
    purchase_request_file = models.FileField(upload_to=file_upload_path, null=True)

    # Relations
    executive = models.ForeignKey(Executive, null=True)
    nda = models.ForeignKey(NDA, null=True)
    statement_of_work = models.ForeignKey(StatementOfWork, null=True)
    consulting_agreement = models.ForeignKey(ConsultingAgreement, null=True)
    # Purchase Request ForeignKey


@receiver(post_save, sender=AbstractUserModel)
def abstract_user_creation(sender, instance, created, **kwargs):
    if created:
        print >> sys.stderr, instance
        print >> sys.stderr, instance.account_type
        if instance.account_type == 'C':
            Client.objects.create(user=instance)
        else:
            Executive.objects.create(user=instance)
