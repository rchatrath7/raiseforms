from django import forms
from django.forms import widgets
from localflavor.us import forms as lf_forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=widgets.PasswordInput)


class ClientForm(forms.Form):
    # TODO: Consolidated address into pieces validated through lfForm Fields
    name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=30, widget=widgets.EmailInput)
    address = forms.CharField(max_length=100)


class NDAForm(forms.Form):
    ssn = lf_forms.USSocialSecurityNumberField()
    corporation = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    title = forms.CharField(max_length=100)
    date = forms.DateTimeField(widget=widgets.SelectDateWidget)


class StatementOfWorkForm(forms.Form):
    desc_of_services = forms.CharField(widget=widgets.Textarea)
    milestone_choices = (
        (False, 'No Milestones are available for this service.'),
        (True, 'The following table contains a high level description of milestone services'),
    )
    deliverables_choices = (
        (False, 'The company and consultant will agree to mutually define deliverables'),
        (True, 'The consultant shall provide the following deliverables on or before the specified dates'),
    )
    fees_choices = (
        (True, 'Time and Materials: Services will be provided on a time and material basis, the Parties will agree on' +
               'the following rates and expected hours per week.'),
        (False, 'All services shall be provided by the Consultant for a defined total cost.')
    )
    milestones = forms.ChoiceField(widget=widgets.RadioSelect, choices=milestone_choices)
    deliverables = forms.ChoiceField(widget=widgets.RadioSelect, choices=milestone_choices)
    fees = forms.ChoiceField(widget=widgets.RadioSelect, choices=fees_choices)
    hourly_rate = forms.FloatField()
    expected_hours_per_week = forms.IntegerField()
    additional_terms_of_services = forms.CharField(widget=widgets.Textarea)


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

