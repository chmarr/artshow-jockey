from django.contrib import admin, messages
from tinyannounce.models import *

class AnnouncementSeenInline(admin.TabularInline):
    model = AnnouncementSeen


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject', 'author', 'important', 'created', 'expires')
    search_fields = ('subject', 'body')
    list_filter = ('important', )
    inlines = [AnnouncementSeenInline]


admin.site.register(Announcement, AnnouncementAdmin)
