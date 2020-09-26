from django.urls import path,include
from facebook_auth import views
from django.conf import settings
from django.conf.urls.static import static


app_name = 'facebook_auth'

urlpatterns = [
    path('',views.welcome_page,name='welcome_page'),
    path('send_mail/',views.send_mail,name='send_mail'),
    path('getdata/',views.get_data,name='getdata'),
    path('home/',views.home,name='home'),
    path('home/data_table',views.data_table,name='data_table'),
    path('home/page_view/<pageId>/',views.Page_View_Logged_Logout.as_view(),name='Page_View_Logged_Logout'),
    path('home/upload_pic',views.upload_pic,name='upload_pic'),
    path('home/page',views.dashbaord_page,name='page'),
    path('home/export',views.csv_export,name='export'),
    path('home/export_excel',views.excel_export,name='export_excel'),
    path('home/report',views.report,name='report'),
    path('home/about_tool',views.about_tool,name='about_tool'),
    path('home/edit_profile',views.edit_profile,name='edit_profile'),
    path('home/adaccount',views.dashbaord_adaccount,name='adaccount'),
    path('home/synchronous',views.synchronous_data,name='synchronous'),
    path('home/experience',views.campaigns_experience,name='experience'),
    path('home/adaccount/campaign_details',views.campaign_detail,name='campaign_details'),
    path('home/adaccount/campaign_ads_insights/<ad_Id>/',views.Campaign_Ads_Insights.as_view(),name='campaign_ads_insights'),
    path('page_insight/',views.get_one_page_insight,name='page_insight'),
    path('home/page_metric_choice/<pageId>/<metric>',views.Page_Metric_Choice.as_view(),name='page_metric_choice'),
    path('home/page_impressions/<pageId>/',views.Page_Impressions.as_view(),name='page_impressions'),
    path('home/page_posts_impressions/<pageId>/',views.Page_Posts_Impressions.as_view(),name='page_posts_impressions'),
    path('home/page_view_logged_logout/<pageId>/',views.Page_View_Logged_Logout.as_view(),name='page_view_logged_logout'),
    path('home/page_fans/<pageId>/',views.Page_Fans.as_view(),name='page_fans'),
    path('home/page_feedback/<pageId>/',views.Page_Negative_Feedback.as_view(),name='page_feedback'),
    path('home/page_fans_city/<pageId>/',views.Page_Fans_City.as_view(),name='page_fans_city'),
    path('adaccount_insight/',views.get_one_adaccount_insight,name='adaccount_insight'),
    path('delete_all/',views.delete_all,name='delete_all'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)