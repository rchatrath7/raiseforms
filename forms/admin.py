from django.contrib import admin
from models import Executive, Client, NDA, StatementOfWork, ConsultingAgreement, PurchaseRequest

# Register your models here.
admin.site.register(Executive)
admin.site.register(Client)
admin.site.register(NDA)
admin.site.register(StatementOfWork)
admin.site.register(ConsultingAgreement)
admin.site.register(PurchaseRequest)
