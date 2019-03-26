from django_cron import CronJobBase, Schedule
from django.utils import timezone
from .models import RequestFiles


class RemoveOldSessions(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'website.remove_old_sessions'

    def do(self):
        objs = RequestFiles.objects.filter(date_created__lt=timezone.now() - timezone.timedelta(minutes=1))
        [obj.delete() for obj in objs]

def my_scheduled_job():
    print("kek")