from django.contrib import admin
from .models import Metric,API,Report,PeriodicReport,Logo
# Register your models here.
admin.site.register(Metric)
admin.site.register(API)
admin.site.register(Report)
admin.site.register(PeriodicReport)
admin.site.register(Logo)