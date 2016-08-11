from django.contrib import admin
from models import AbstractUserModel, Executive, Client, NDA, StatementOfWork, ConsultingAgreement, PurchaseRequest


# Defining InlineClasses
class ExecutiveInline(admin.StackedInline):
    model = Executive
    verbose_name_plural = 'executive'


class ClientInline(admin.StackedInline):
    model = Client
    verbose_name_plural = 'client'


# Define new UserAdmin
class UserAdmin(admin.ModelAdmin):
    inlines = (ExecutiveInline, )


# Register your models here.
# admin.site.register(Executive)
# admin.site.register(Client)
admin.site.register(AbstractUserModel, UserAdmin)
admin.site.register(NDA)
admin.site.register(StatementOfWork)
admin.site.register(ConsultingAgreement)
admin.site.register(PurchaseRequest)
