from django.contrib import admin
from .models import *


class InsuranceAdmin(admin.ModelAdmin):
    fields = ['policy_number', 'company']

# Register your models here.
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Insurance, InsuranceAdmin)
admin.site.register(Unit)
