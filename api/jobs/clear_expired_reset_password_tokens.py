from django.core import management
from django_cron import CronJobBase, Schedule


class ClearPasswordResetTokenJob(CronJobBase):
    scheduler = Schedule(run_every_mins=30)
    code = 'api.jobs.ClearPasswordResetTokenJob'

    def do(self):
        management.call_command('clear_password_token')
