from django.utils import timezone
from .models import RequestFiles


def remove_old_sessions():
    objs = RequestFiles.objects.filter(date_created__lt=timezone.now() - timezone.timedelta(minutes=1))
    [obj.delete() for obj in objs]
    print("%s: job finished" % timezone.now())
