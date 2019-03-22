from django.db import models


class RequestFiles(models.Model):
    csrf_id = models.CharField(max_length=200)


class UploadedFile(models.Model):

    def define_upload_path(self, filename):
        return f"uploads/{self.request_session.csrf_id}/{filename}"

    request_session = models.ForeignKey(RequestFiles, on_delete=models.CASCADE, related_name='uploaded_files')
    filename = models.FileField(upload_to=define_upload_path)
