from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from .models import RequestFiles, UploadedFile, Statistic


class RequestFilesInlineAdmin(admin.TabularInline):
    model = UploadedFile


@admin.register(RequestFiles)
class RequestFilesAdmin(admin.ModelAdmin):
    inlines = [RequestFilesInlineAdmin]
    list_display = ['csrf_id', 'date_created', 'until_deleted']

    def until_deleted(self, obj):
        minutes_since_added = ((timezone.now() - obj.date_created).seconds // 60) % 60
        return "%s min" % (settings.REMOVE_OLD_SESSION - minutes_since_added)


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ['output_filename', 'date_created', 'ip_address', 'tool_type']
    list_filter = ['date_created', 'tool_type']
