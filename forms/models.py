from __future__ import unicode_literals
from django.db import models

# Create your models here.


class Executive(models.Model):
    # Raise executive. We need to get the name and email of the Raise executive for use when signing the docusign
    # document.
    # TODO: Adding more fields and any necessary methods. Make a more secure way of hasing and storing passwords.
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=30)
    username = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    # We need to use a better way of storing the password - Use hashing algorithm and some sort of setter
    password = models.CharField(max_length=16)

    # Relations
    # client = models.ForeignKey('Client')

    def __str__(self):
        return "<Name: " + self.name +" Email: " + self.email + ">"


class Client(models.Model):
    # The client is the person signing. We want to be able to send them multiple forms if possible, as well as gather
    # All necessary information at once.
    # TODO: Figure out file uploading/googledocs support.
    def file_upload_path(self, instance, filename):
        # Upload file to MEDIA_ROOT/user.id/filename
        # Perhaps adjust for renaming the files from something less ugly to something more readable - maybe the file ID
        # We could also remove all file handling to the individual classes
        return str(self.id)+'/'+filename

    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=30)
    address = models.CharField(max_length=100)
    nda = models.FileField(upload_to=file_upload_path)
    statement_of_work = models.FileField(upload_to=file_upload_path)
    consulting_agreement = models.FileField(upload_to=file_upload_path)
    purchase_request = models.FileField(upload_to=file_upload_path)

    # Relations
    # executive = models.ForeignKey(Executive)

    def __str__(self):
        return "<Name: " + self.name + " Email: " + self.email + ">"


class NDA(models.Model):
    # TODO: Put in validators
    # NDA FORM
    ssn = models.CharField(max_length=9)
    location = models.CharField(max_length=100)
    corporation = models.CharField(max_length=100)
    title = models.CharField(max_length=20)
    agreement_date = models.DateTimeField(auto_now_add=True)

    # Relations
    # client = models.ForeignKey(Client)
    # executive = models.ForeignKey(Executive)


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


class ConsultingAgreement(models.Model):
    agreement_date = models.DateTimeField(auto_now_add=True)


class PurchaseRequest(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    cost_center = models.CharField(max_length=50)
    # Client/Owner
    requester = models.ForeignKey(Client)
    owner = models.ForeignKey(Executive)
    vendor = models.CharField()
    description = models.TextField()
    purpose = models.TextField()
    amount = models.FloatField()
    # This should be a date range, just adjust it to get the difference in time
    service_period = models.DateTimeField()
    # Handle 'either-ors' better (invoice, payment_type, etc)
    contract_present = models.BooleanField(default=False)
    invoice_cadence_recurring = models.BooleanField(default=False)
    if invoice_cadence_recurring:
        recurring_date = models.DateTimeField()
    payment_types = {
        'ach': models.BooleanField(default=False),
        'credit': models.BooleanField(default=False),
        'check': models.BooleanField(default=False),
        'abacus': models.BooleanField(default=False)
    }
    payment_terms_net_30 = models.BooleanField(default=False)
    payment_terms_receipt = models.BooleanField(default=False)

    additional_notes = models.TextField()



