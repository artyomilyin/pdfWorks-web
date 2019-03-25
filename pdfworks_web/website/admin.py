from django.contrib import admin
from .models import RequestFiles, UploadedFile


class RequestFilesInlineAdmin(admin.TabularInline):
    model = UploadedFile


@admin.register(RequestFiles)
class RequestFilesAdmin(admin.ModelAdmin):
    inlines = [RequestFilesInlineAdmin]
