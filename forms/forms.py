from django import forms
from django.forms import widgets, ModelForm
from models import *
from localflavor.us import forms as lf_forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

class ClientForm(forms.Form):
    # TODO: Consolidated address into pieces validated through lfForm Fields
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'pure-u-1'}))
    email = forms.EmailField(widget=widgets.EmailInput(attrs={'class': 'pure-u-1'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))


class ManageClientForm(ModelForm):
    updated = []

    class Meta:
        model = Client
        fields = ['address']

    def clean(self):
        self.updated = []
        cleaned_data = super(ManageClientForm, self).clean()
        if self.instance.pk is not None:
            for field, value in self.fields.iteritems():
                if getattr(self.instance, field) != cleaned_data[field]:
                    self.updated.append(field)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(ManageClientForm, self).__init__(*args, **kwargs)
        for key, value in self.fields.iteritems():
            self.fields[key].widget.attrs['class'] = 'pure-u-23-24'


class ManageUserForm(ModelForm):
    updated = []
    password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'pure-u-23-24'}), required=False)
    new_password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'pure-23-24'}), required=False)
    confirm_password = forms.CharField(widget=widgets.PasswordInput(attrs={'class': 'pure-23-24'}), required=False)

    class Meta:
        model = AbstractUserModel
        fields = ['email', 'first_name', 'last_name']

    def clean(self):
        self.updated = []
        cleaned_data = super(ManageUserForm, self).clean()
        if self.instance.pk is not None:
            for field, value in self.fields.iteritems():
                if field not in ['password', 'new_password', 'confirm_password']:
                    if getattr(self.instance, field) != cleaned_data[field]:
                        self.updated.append(field)
                else:
                    if cleaned_data[field] is not None:
                        self.updated.append(field)
        return cleaned_data

    def save(self, commit=True):
        user = super(ManageUserForm, self).save(commit=False)
        password = self.cleaned_data["password"]
        new_password = self.cleaned_data["new_password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if password and new_password and confirm_password:
            if user.check_password(password) and new_password == confirm_password:
                user.set_password(new_password)
        if commit:
            user.save()
        return user


    def __init__(self, *args, **kwargs):
        super(ManageUserForm, self).__init__(*args, **kwargs)
        for key, value in self.fields.iteritems():
            self.fields[key].widget.attrs['class'] = 'pure-u-23-24'


class ContactForm(forms.Form):
    to = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    cc = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}), required=False)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'pure-u-1'}))


class NDAForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    email = forms.EmailField(widget=widgets.EmailInput(attrs={'class': 'pure-u-1'}))
    ssn = lf_forms.USSocialSecurityNumberField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    corporation = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))


class StatementOfWorkForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'pure-u-1'}))
    email = forms.EmailField(widget=widgets.EmailInput(attrs={'class': 'pure-u-1'}))
    desc_of_services = forms.CharField(widget=widgets.Textarea(attrs={'class': 'pure-u-1'}))
    milestone_choices = (
        (False, 'No Milestones are available for this service.'),
        (True, 'The following table contains a high level description of milestone services'),
    )
    deliverables_choices = (
        (False, 'The company and consultant will agree to mutually define deliverables'),
        (True, 'The consultant shall provide the following deliverables on or before the specified dates'),
    )
    fees_choices = (
        (True, 'Time and Materials: Services will be provided on a time and material basis, the Parties will agree on ' +
               'these rates and expected hours per week.'),
        (False, 'All services shall be provided by the Consultant for a defined total cost.')
    )
    milestones = forms.ChoiceField(widget=widgets.RadioSelect(attrs={'class': 'pure-radio', 'style': 'width: auto'}), choices=milestone_choices)
    deliverables = forms.ChoiceField(widget=widgets.RadioSelect(attrs={'class': 'pure-radio', 'style': 'width: auto'}), choices=deliverables_choices)
    fees = forms.ChoiceField(widget=widgets.RadioSelect(attrs={'class': 'pure-radio', 'style': 'width: auto'}), choices=fees_choices)
    hourly_rate = forms.FloatField(widget=widgets.TextInput(attrs={'class': 'pure-u-1'}))
    expected_hours_per_week = forms.IntegerField(widget=widgets.TextInput(attrs={'class': 'pure-u-1'}))
    additional_terms_of_services = forms.CharField(widget=widgets.Textarea(attrs={'class': 'pure-u-1'}))


class ConsultingAgreementForm(forms.Form):
    agreement_date = forms.DateTimeField(widget=widgets.DateTimeBaseInput)


class PurchaseRequestForm(forms.Form):
    cost_center = forms.CharField(max_length=100)
    description = forms.Textarea()
    purpose = forms.TextInput()
    amount = forms.FloatField()
    service_period = forms.SplitDateTimeField(widget=widgets.SplitDateTimeWidget)
    contract_present = forms.ChoiceField(widget=widgets.CheckboxInput)
    invoice_cadence_recurring = forms.ChoiceField(widget=widgets.CheckboxInput)
    recurring_date = forms.DateTimeField(widget=widgets.SelectDateWidget)
    payment_choices = (
        ('ach', 'ACH'),
        ('credit', 'Credit'),
        ('check', 'Check'),
        ('abacus', 'Abacus')
    )
    payment_type = forms.ChoiceField(widget=widgets.RadioSelect, choices=payment_choices)
    payment_net_30 = forms.ChoiceField(widget=widgets.CheckboxInput)
    payment_terms_receipt = forms.ChoiceField(widget=widgets.CheckboxInput)
    additional_notes = forms.CharField(widget=widgets.Textarea)


# Modified password reset form
class NewPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, _is_active=True)
        return (u for u in active_users if u.has_usable_password())

