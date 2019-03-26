from django.contrib import admin
from django.utils import timezone
from .models import RequestFiles, UploadedFile
from .cron import RemoveOldSessions


class RequestFilesInlineAdmin(admin.TabularInline):
    model = UploadedFile


@admin.register(RequestFiles)
class RequestFilesAdmin(admin.ModelAdmin):
    inlines = [RequestFilesInlineAdmin]
    list_display = ['csrf_id', 'date_created', 'until_deleted']

    def until_deleted(self, obj):
        minutes_since_added = ((timezone.now() - obj.date_created).seconds // 60) % 60
        return "%s min" % (RemoveOldSessions.RUN_EVERY_MINS - minutes_since_added)
