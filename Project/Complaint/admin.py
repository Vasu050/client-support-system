from django.contrib import admin
from .models import Complaints
# Register your models here.
class ComplaintsAdmin(admin.ModelAdmin):
    readonly_fields = ['client']
    
    list_display = ('id','client','status')

admin.site.register(Complaints,ComplaintsAdmin)