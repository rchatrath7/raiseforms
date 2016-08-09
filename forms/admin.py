from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
from models import Executive, Client, NDA, StatementOfWork, ConsultingAgreement, PurchaseRequest


# Defining InlineClasses
class ExecutiveInline(admin.StackedInline):
    model = Executive
    verbose_name_plural = 'executive'


class ClientInline(admin.StackedInline):
    model = Client
    verbose_name_plural = 'client'


# Define new UserAdmin
class UserAdmin(UserAdmin):
    inlines = (ExecutiveInline, )


# Register your models here.
# admin.site.register(Executive)
# admin.site.register(Client)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(NDA)
admin.site.register(StatementOfWork)
admin.site.register(ConsultingAgreement)
admin.site.register(PurchaseRequest)
