from django.contrib import admin
from .models import Specialist


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    list_filter = ('name',)
    search_fields = ('name', 'image')
    list_editable = ('image',)
    list_per_page = 25