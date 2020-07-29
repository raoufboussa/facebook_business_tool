from django.db import models
import os,time
# Create your models here.
class API(models.Model):
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)

class Metric(models.Model):
    name = models.CharField(max_length=100)
    API = models.ForeignKey(API,on_delete=models.PROTECT) # will raise an error when trying to delete API
    queryName = models.CharField(max_length=100)
from django.contrib.auth.models import User
class Report(models.Model):
    name = models.CharField(max_length=100,null=True)
    report = models.CharField(max_length=10000)
    API = models.ForeignKey(API,on_delete=models.PROTECT)
    user =  models.ForeignKey(User,on_delete=models.CASCADE, default = None)
    createdDate = models.DateTimeField(auto_now=True)
    lastModifiedDate = models.DateTimeField(auto_now_add=True)
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
class PeriodicReport(models.Model):
    name = models.CharField(max_length=100,null=True)
    report =  models.ForeignKey(Report,on_delete=models.CASCADE, default = None)
    periodInDays = models.IntegerField(validators=[
                                            MaxValueValidator(91),
                                            MinValueValidator(7)]) # entre une semaine et 3 mois ?
    createdDate = models.DateTimeField(auto_now=True)
    nextRunDate = models.DateField()
    emailAddress= models.EmailField()


def get_image_path(instance, filename):
    return os.path.join('logos',  str(int(time.time()))+'_'+filename)
class Logo(models.Model):
    logo = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    user =  models.OneToOneField(User,on_delete=models.CASCADE, default = None)
    def save(self):
        super(Logo, self).save()
        #resize image so it has a size that won't cause problems with phantomjs
        from PIL import Image
        im = Image.open('./assets/'+str(self.logo))
        im = im.resize((100,100),Image.ANTIALIAS)
        im.save('./assets/'+str(self.logo))

#apply the following in console to migrate and update :
#python manage.py makemigrations
#python manage.py migrate
#apply this in manage.py shell
# from pseudoAPI.models import API, Metric
# a1 = API(name="FacebookGraph",provider="Facebook")
# a2 = API(name="FacebookAds",provider="Facebook")
# a3 = API(name="AdWords",provider="Google")
# a1.save()
# a2.save()
# a3.save()
#
# m1 = Metric(name="Vues de Page", API= a1,queryName= 'page_views_total')
# m1.save()
# m2 = Metric(name="Impressions de Page", API= a1,queryName= 'page_impressions')
# m2.save()
# m3 = Metric(name="Vues Videos", API= a1,queryName= 'page_video_views')
# m3.save()
# m4 = Metric(name="Reach", API= a2,queryName= 'reach')
# m4.save()
# m5 = Metric(name="cpm", API= a2,queryName= 'cpm')
# m5.save()
# m6 = Metric(name="cpc", API= a2,queryName= 'cpc')
# m6.save()
# m7 = Metric(name="Impressions", API= a2,queryName= 'impressions')
# m7.save()

#to fetch all
#Metric.objects.all()
#to delte all
#Metric.objects.all().delete()
