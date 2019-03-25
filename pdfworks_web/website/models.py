import os
import shutil

from django.db import models


class RequestFiles(models.Model):
    csrf_id = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.csrf_id} request"

    def delete(self, output_filename=None, using=None, keep_parents=False):
        if self.uploaded_files:
            shutil.rmtree(f'uploads/{self.csrf_id}')
            os.remove(output_filename)
        super(RequestFiles, self).delete(using=using, keep_parents=keep_parents)

    class Meta:
        verbose_name_plural = 'Request files'


class UploadedFile(models.Model):

    def define_upload_path(self, filename):
        return f"uploads/{self.request_session.csrf_id}/{filename}"

    request_session = models.ForeignKey(RequestFiles, on_delete=models.CASCADE, related_name='uploaded_files')
    filename = models.FileField(upload_to=define_upload_path)
    uuid = models.CharField(max_length=200, db_index=True)

    class Meta:
        ordering = ('id',)
