from django.contrib import admin

from .models import Person


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_id', 'email')
    search_fields = ('name', 'reg_id', 'email')
    list_filter = ('country', )


admin.site.register(Person, PersonAdmin)
