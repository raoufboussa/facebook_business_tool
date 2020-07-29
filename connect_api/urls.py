from django.conf import settings
from django.conf.urls.static import static
from django.urls import *
from FacebookOAuth.views import *
from pseudoAPI.views import *
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('',include('facebook_auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('report',report),
    path('profile/',profile),
    # path('',index),
    path('facebookAPI', getFacebookData),
    path('facebookPageViews', facebookInsightsViews),
    path('facebookOneNumberMetric', facebookOneNumberMetric),
    path('facebookAds',facebookAds),
    path('facebookAdsRelevanceScores',facebookAdsRelevanceScores),
    path('chooseAccount',chooseAccount),
    path('googleAnalyticsNumber', googleAnalyticsNumber),
    path('googleAnalyticsLine', googleAnalyticsWithDimensions),
    path('googleAdsNumber', googleAdsNumber),
    path('googleAdsDimension', googleAdsWithDimensions),
    path('googleTest', profileGoogle),
    path('chokri',chaouki),
    path('moncef',moncef_test),
    path('prepareReport',prepareReport),
    path('facebookAdsBodyAndScore',facebookAdsBodyAndScore),
    path('saveReport',saveReport),
    path('loadReport',loadReport),
    path('reportList', ReportList.as_view()),
    path('sendEmail',sendEmail),
    path('downloadReport',downloadReport),
    path('sendEmailPhantom',sendEmailPhantom),
    path('LogoCreate',LogoCreate.as_view()),
    path('LogoUpdate',LogoUpdate.as_view()),
    path('PeriodicReportCreate',PeriodicReportCreate.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
