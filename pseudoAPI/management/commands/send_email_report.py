from django.core.management.base import BaseCommand
from django.utils import timezone
from pseudoAPI.views import sendEmailReportCommand
from pseudoAPI.models import PeriodicReport
from datetime import date,timedelta
class Command(BaseCommand):
    help = 'Send a pdf report via email'
    # def add_arguments(self, parser):
    #     parser.add_argument('periodicId', type=int, help='the id of the PeriodicReport')
    def handle(self, *args, **kwargs):
        #periodicId = kwargs['periodicId']
        periodics= PeriodicReport.objects.all()
        for p in periodics:

            print("nextrun: ", p.nextRunDate,"today :", date.today(),"period: ", p.periodInDays, "nextrun+period: " ,p.nextRunDate+ timedelta(days=p.periodInDays),p.nextRunDate==date.today())
            print("email for periodic *" + p.name+"* is sent ")
            if p.nextRunDate==date.today():
                sendEmailReportCommand(p.id)
                #if mail succesful
                p.nextRunDate = p.nextRunDate+ timedelta(days=p.periodInDays)
                p.save()
