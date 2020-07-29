from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.translation import gettext as _
from django.shortcuts import render,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.models import User
from bson.json_util import dumps
from .forms import ImageUploadForm,Experience_Campain,Edit_Profile,UserForm,Experience_Mode,Export_Form
from .models import (
    Campaign, Account_Page, API, Ad_Account,Cover_Photo,Action,Attribution_Spec,Post,
    Ad_Account_Insight,Cost_Per_Action_Type,Cost_Per_Outbound_Click,Ad_Targeting,Post_actions,
    Cost_Per_Unique_Action_Type,Cost_Per_Unique_Outbound_Click,Ad as Ads,Ad_Insight,
    Outbound_Clicks_Ctr, Cost_Per_Thruplay,Metric, Page_Insight,Insights_Value,API,UserProfile
    ,Experience_Campaign)
from rest_framework.views import APIView
from rest_framework.response import Response
import facebook,json as JSON,requests,time,os,csv
from datetime import datetime
from math import ceil
import datetime
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.pagepost import PagePost
from facebook_business.adobjects.business import Business
from facebook_business.adobjects.customaudienceadaccount import CustomAudienceAdAccount
from facebook_business.adobjects.insightsresult import InsightsResult
from facebook_business.adobjects.instagraminsightsvalue import InstagramInsightsValue
from facebook_business.adobjects.instagramuser import InstagramUser
from facebook_business.adobjects.instagramcomment import InstagramComment
from facebook_business.adobjects.campaign import Campaign as AdCampaign
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adset import AdSet
from facebook_scraper import get_posts
from allauth.socialaccount.models import (
    SocialAccount,
    SocialApp,
    SocialToken
    )

def login_page(request):
    # if(request.user):
    #     utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
    #     utilisateur.save()

    return render(request,'welcome_page.html',locals())

@login_required
@transaction.atomic
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = Edit_Profile(request.POST, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('facebook_auth:home')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = Edit_Profile(instance=request.user.userprofile)
    return render(request, 'account/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
            
            
    return render(request,'upload_img.html', locals())
def csv_export(request):
    utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
    utilisateur.save()
    if request.method == 'POST':
        form = Export_Form(request.POST)
        if (form.is_valid()):
            model = request.POST['model']
            response = HttpResponse(content_type='text/csv')
            if (model =="Campaigns"):
                response['Content-Disposition'] = 'attachment;filename="campaigns.csv"'
                writer = csv.writer(response)
                writer.writerow(["Name" ,"Objective","Niche","Age_max","Age_min","Genders","Created_Time",
                "CPC","CPM","CPP","Clicks","Frequency","CTR","Location_Types","Country","Citie","Region",
                "Device_Platforms","Publisher_Platforms","Positions","Efficiency"])
                objects = Experience_Campaign.objects.all().values_list("name" ,"objective","niche","age_max","age_min","genders","created_time",
                "cpc","cpm","cpp","clicks","frequency","ctr","location_types","country","citie","region",
                "device_platforms","publisher_platforms","positions","efficiency")
            if (model =="Pages"):
                response['Content-Disposition'] = 'attachment;filename="pages.csv"'
                writer = csv.writer(response)
                writer.writerow(["Access_Token" ,"Category","Cover","Phone","Unseen_Message_Count",
                "Unread_Message_Count","Rating_Count","Unread_Notif_Count","Talking_About_Count","New_Like_Count","Fan_Count","Is_Owned",
                "Name_With_Location_Descriptor","Offer_Eligible" ,"Overall_Star_Rating" , "Website","Supports_Instant_Articles","About","Verification_Status"
                ,"Last_Update"])
                objects = Account_Page.objects.all().values_list("access_token" ,"category","cover","phone","unseen_message_count",
                "unread_message_count","rating_count","unread_notif_count","talking_about_count","new_like_count","fan_count","is_owned",
                "name_with_location_descriptor","offer_eligible" ,"overall_star_rating" , "website","supports_instant_articles","about","verification_status"
                ,"last_update" )

            if (model =="Ad_accounts"):
                response['Content-Disposition'] = 'attachment;filename="ad_accounts.csv"'
                writer = csv.writer(response)
                writer.writerow(["Name" ,"Account_Status","Created_time","Owner_Id","Age","Amount_Spent","Attribution_Spec","Balance",
                "Can_Create_Brand_Lift_Study","Capabilities","Last_Update","Last_Update_Campaigns" ])
                objects = Ad_Account.objects.all().values_list("name" ,"account_status","created_time","owner_id","age",
                "amount_spent","attribution_spec","balance","can_create_brand_lift_study","capabilities","last_update","last_update_campaigns"  )
            for obj in objects:
                writer.writerow(obj)
            return response
    else:
        form = Export_Form()
        return render(request, 'export_csv.html',locals())

def about_tool(request):
    utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
    utilisateur.save()

    return render(request,"about_tool.html",locals())
        

@login_required
def get_data(request):
    cef = User.objects.filter(username =str(request.user))[0]
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret) 
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    me = AdUser(fbid='me')


    #-----------------------------------------------data of pages------------------------------------------------


    my_pages = me.get_pages(fields=[Page.Field.name,Page.Field.id,Page.Field.new_like_count,
    Page.Field.access_token,Page.Field.category,Page.Field.fan_count,Page.Field.is_owned,
    Page.Field.name_with_location_descriptor,Page.Field.network,Page.Field.offer_eligible,
    Page.Field.page_token,Page.Field.cover,Page.Field.about,Page.Field.phone,
    Page.Field.rating_count,
    Page.Field.parent_page,Page.Field.parking,Page.Field.payment_options,
    Page.Field.personal_info,Page.Field.personal_interests,Page.Field.whatsapp_number,
    Page.Field.were_here_count,Page.Field.website,Page.Field.voip_info,
    Page.Field.verification_status,Page.Field.username,Page.Field.unseen_message_count,
    Page.Field.unread_notif_count,Page.Field.unread_message_count,Page.Field.talking_about_count,
    Page.Field.supports_instant_articles,Page.Field.studio,Page.Field.store_number,
    Page.Field.store_location_descriptor,Page.Field.store_code,Page.Field.schedule
    ])
    #---------------------------------------------data of adaccount-----------------------------------------------#
    # my_ad_account = me.get_ad_accounts(fields=[AdAccount.Field.name,AdAccount.Field.id,
    # AdAccount.Field.account_id,AdAccount.Field.account_status,
    # AdAccount.Field.ad_account_creation_request,
    # AdAccount.Field.ad_account_promotable_objects,
    # AdAccount.Field.age,AdAccount.Field.agency_client_declaration,
    # AdAccount.Field.amount_spent,AdAccount.Field.attribution_spec,AdAccount.Field.balance,AdAccount.Field.business,  ######## proprietées pour l'admin de l'entreprise
    # AdAccount.Field.business_city,AdAccount.Field.business_country_code,AdAccount.Field.business_name,               ######## must be business admin of your Business Manager to call this API
    # AdAccount.Field.business_state,AdAccount.Field.business_street,AdAccount.Field.business_street2,
    # AdAccount.Field.business_zip,AdAccount.Field.can_create_brand_lift_study,AdAccount.Field.capabilities
    # ])
    import requests

    params = (
        ('fields', 'adaccounts{name,id,account_id,balance,age,capabilities,created_time,owner,insights{actions,action_values,clicks,account_name,date_start,date_stop,cost_per_conversion,cost_per_action_type,cost_per_estimated_ad_recallers,cost_per_inline_link_click,cost_per_inline_post_engagement,cost_per_thruplay,cost_per_outbound_click,cost_per_unique_click,cost_per_unique_action_type,cost_per_unique_outbound_click,cost_per_unique_inline_link_click,conversion_values,conversions,canvas_avg_view_percent,canvas_avg_view_time,outbound_clicks_ctr,objective,campaign_id,campaign_name},agency_client_declaration,amount_spent,attribution_spec,can_create_brand_lift_study}'),
        ('access_token', my_access_token),
    )

    response = requests.get('https://graph.facebook.com/v5.0/me', params=params)
    print("9awed")
    print(type(response))
    my_ad_account = response.json()
    namesAndAccIds = []
    namesAndAdaccIDs = []
    account_insieght = []
    page_likes = []
    for account in my_pages:
        page,created = Account_Page.objects.get_or_create(page_id=str(account['id']))
        namesAndAccIds.append((account['name'],account['id'],account['access_token']))
        cover,created = Cover_Photo.objects.get_or_create(id = account['cover']['id'])       
        if ('cover' in account):
            cover.id = account['cover']['id']
            cover.page_name = account['name']
            cover.offset_x = account['cover']['offset_x']
            cover.offset_y = account['cover']['offset_y']
            cover.source = account['cover']['source']
            cover.save()
            page.cover_photo = cover
            
        page.name = account['name']
        page.page_id = account['id']
        if ('talking_about_count' in account):
            page.talking_about_count = account['talking_about_count']
        if('phone' in account):
            page.phone = account['phone']
        page.unseen_message_count = account['unseen_message_count']
        page.unread_message_count = account['unread_message_count']
        page.unread_notif_count = account['unread_notif_count']
        page.access_token = account['access_token']
        page.category = account['category']
        page.fan_count = account['fan_count']
        page.new_like_count = account['new_like_count']
        page.is_owned = account['is_owned']
        page.name_with_location_descriptor = account['name_with_location_descriptor']
        page.offer_eligible = account['offer_eligible']
        page.supports_instant_articles = account['supports_instant_articles']
        page.verification_status = account['verification_status']
        if ('website' in account):
            page.website = account['website']
        if ('about' in account):
            page.about = account['about']
        page.save()
    for adaccount in my_ad_account['adaccounts']['data']:
        namesAndAdaccIDs.append((adaccount['name'],adaccount['id']))
        adAccount,created = Ad_Account.objects.get_or_create(adaccount_id=str(adaccount['id']))
        adAccount.name = adaccount['name']
        adAccount.adaccount_id = adaccount['id']
        adAccount.id = adaccount['account_id']
        if ('balance' in adaccount):
            adAccount.balance = adaccount['balance']
        if ('age' in adaccount):
            adAccount.age = adaccount['age']
        if ('capabilities' in adaccount):
            adAccount.capabilities = adaccount['capabilities']
        if ('created_time' in adaccount):
            adAccount.created_time = adaccount['created_time']
        if ('owned' in adaccount):
            adAccount.owner_id = adaccount['owned']
        if ('amount_spent' in adaccount):
            adAccount.amount_spent = adaccount['amount_spent']
        if ('can_create_brand_lift_study' in adaccount):
            adAccount.can_create_brand_lift_study = adaccount['can_create_brand_lift_study']
        if ('account_status' in adaccount):
            adAccount.account_status = adaccount['account_status']


        adAccount.save()
        ###################################################attribution_spec##################################################
        if ('attribution_spec' in adaccount):
            for attribution_spec_pool in adaccount['attribution_spec']:
                attribution_spec,created = Attribution_Spec.objects.get_or_create(attribution_spec_id = adaccount['name'],event_type = attribution_spec_pool['event_type'])
                attribution_spec.event_type = attribution_spec_pool['event_type']
                attribution_spec.attribution_spec_id = adaccount['name']
                attribution_spec.window_days = attribution_spec_pool['window_days']
                attribution_spec.save()
                adAccount.attribution_spec.add(attribution_spec)
        ###################################################collect the insight of ad_account#################################################
        if ('insights' in adaccount):
            for insights in adaccount['insights']['data']:

                ad_account_insight = Ad_Account_Insight()
                ad_account_insight.clicks = insights['clicks']
                ad_account_insight.account_name = insights['account_name']
                ad_account_insight.save()
                
                for action_pool in insights["actions"]:
                    action,created = Action.objects.get_or_create(action_id = adaccount['name'],action_type = action_pool['action_type'])
                    action.action_type = action_pool['action_type']
                    action.action_id = adaccount['name']
                    action.value = action_pool['value']
                    action.save()
                    ad_account_insight.actions.add(action)
                
                for cost_per_action_type_pool in insights["cost_per_action_type"]:
                    cost_per_action_type,created = Cost_Per_Action_Type.objects.get_or_create(cost_per_action_type_id=(adaccount['name']+"/"+cost_per_action_type_pool['action_type']+"/"+cost_per_action_type_pool['value']))
                    cost_per_action_type.action_type = cost_per_action_type_pool['action_type']
                    cost_per_action_type.value = cost_per_action_type_pool['value']
                    cost_per_action_type.save()
                    ad_account_insight.cost_per_action_type.add(cost_per_action_type)
                if ('cost_per_inline_link_click' in insights):
                    ad_account_insight.cost_per_inline_link_click = insights['cost_per_inline_link_click']
                
                if ('cost_per_inline_post_engagement' in insights):
                    ad_account_insight.cost_per_inline_post_engagement = insights['cost_per_inline_post_engagement']
                
                if ('cost_per_outbound_click' in insights):
                    for cost_per_outbound_click_pool in insights["cost_per_outbound_click"]:
                        cost_per_outbound_click,created = Cost_Per_Outbound_Click.objects.get_or_create(cost_per_outbound_click_id=adaccount['name'],action_type=cost_per_outbound_click_pool['action_type'])
                        cost_per_outbound_click.action_type = cost_per_outbound_click_pool['action_type']
                        cost_per_outbound_click.cost_per_outbound_click_id = adaccount['name']
                        cost_per_outbound_click.value = cost_per_outbound_click_pool['value']
                        cost_per_outbound_click.save()
                        ad_account_insight.cost_per_outbound_click.add(cost_per_outbound_click)

                if ('cost_per_unique_action_type' in insights):
                    for cost_per_unique_action_type_pool in insights["cost_per_unique_action_type"]:
                        cost_per_unique_action_type,created = Cost_Per_Unique_Action_Type.objects.get_or_create(cost_per_unique_action_type_id=adaccount['name'],action_type=cost_per_unique_action_type_pool['action_type'])
                        cost_per_unique_action_type.action_type = cost_per_unique_action_type_pool['action_type']
                        cost_per_unique_action_type.cost_per_unique_action_type_id = adaccount['name']
                        cost_per_unique_action_type.value = cost_per_unique_action_type_pool['value']
                        cost_per_unique_action_type.save()
                        ad_account_insight.cost_per_unique_action_type.add(cost_per_unique_action_type)

                if ('cost_per_unique_click' in insights):
                    ad_account_insight.cost_per_unique_click = insights['cost_per_unique_click']

                if ('cost_per_unique_inline_link_click' in insights):
                    ad_account_insight.cost_per_unique_inline_link_click = insights['cost_per_unique_inline_link_click']
                
                if ('cost_per_unique_outbound_click' in insights):
                    for cost_per_unique_outbound_click_pool in insights["cost_per_unique_outbound_click"]:
                        cost_per_unique_outbound_click,created = Cost_Per_Unique_Outbound_Click.objects.get_or_create(cost_per_unique_outbound_click_id=adaccount['name'],action_type=cost_per_unique_outbound_click_pool['action_type'])
                        cost_per_unique_outbound_click.action_type =cost_per_unique_outbound_click_pool['action_type']
                        cost_per_unique_outbound_click.cost_per_unique_outbound_click_id = adaccount['name']
                        cost_per_unique_outbound_click.value = cost_per_unique_outbound_click_pool['value']
                        cost_per_unique_outbound_click.save()
                        ad_account_insight.cost_per_unique_outbound_click.add(cost_per_unique_outbound_click)
                
                if ('cost_per_thruplay' in insights):
                    for cost_per_thruplay_pool in insights["cost_per_thruplay"]:
                        cost_per_thruplay,created = Cost_Per_Thruplay.objects.get_or_create(cost_per_thruplay_id=(adaccount['name']+"/"+cost_per_thruplay_pool['action_type']+"/"+cost_per_thruplay_pool['value']))
                        cost_per_thruplay.action_type = cost_per_thruplay_pool['action_type']
                        cost_per_thruplay.value = cost_per_thruplay_pool['value']
                        cost_per_thruplay.save()
                        ad_account_insight.cost_per_thruplay.add(cost_per_thruplay)

                if('date_start' in insights):
                    ad_account_insight.date_start = insights['date_start']
                    ad_account_insight.date_stop = insights['date_stop']

                if('objective' in insights):
                    ad_account_insight.objective = insights['objective']

                if ('outbound_clicks_ctr' in insights):
                    for outbound_clicks_ctr_pool in insights["outbound_clicks_ctr"]:
                        outbound_clicks_ctr,created = Outbound_Clicks_Ctr.objects.get_or_create(outbound_clicks_ctr_id=adaccount['name'],action_type=outbound_clicks_ctr_pool['action_type'])
                        outbound_clicks_ctr.action_type = outbound_clicks_ctr_pool['action_type']
                        outbound_clicks_ctr.outbound_clicks_ctr_id = adaccount['name']
                        outbound_clicks_ctr.value = outbound_clicks_ctr_pool['value']
                        outbound_clicks_ctr.save()
                        ad_account_insight.outbound_clicks_ctr.add(outbound_clicks_ctr)
                ad_account_insight.save()
                adAccount.insights = ad_account_insight
                adAccount.save()
            ####################################################### fin de traitement de insights #########################################################
        else: 
            adAccount.save()
    ########################################################### get insights pour chaque page facebook ##########################################################
    for page in namesAndAccIds:
        graphPage = facebook.GraphAPI(access_token=page[2],version="2.9")
        pageId = page[1]
        print(page[0])
        page,created = Account_Page.objects.get_or_create(page_id=str(pageId))
        api = API.objects.filter(name="FacebookGraph",provider="Facebook")
        queryset = Metric.objects.filter(API=api[0])
        for metric in queryset:
            e = time.time() #page_tab_views_login_top&since='+s+'&until='+e+"&period=day
            s = time.time()-(90*24*3600) #on retranche le nombe de seconde dans un mois 
            e,s=str(ceil(e)),str(ceil(s))
            returnedAPIData = graphPage.get_connections(id=pageId, connection_name='insights?metric='+metric.queryName+'&since='+s+'&until='+e+'&period=day')
            print(metric.queryName)
            for element in returnedAPIData['data']:
                page_insight,created = Page_Insight.objects.get_or_create(page_insights_id=element['id'])
                page_insight.page_insights_id = element['id']
                page_insight.name = element['name']
                page_insight.period = element['period'] 
                page_insight.title = element['title']
                page_insight.description = element  ['description']
                for value in element['values']:
                    insight_value,created = Insights_Value.objects.get_or_create(insight_name=element['name'],end_time=value['end_time'],insights_value_id=pageId)
                    insight_value.insights_value_id = pageId
                    insight_value.value = str(value['value'])
                    insight_value.end_time = value['end_time']
                    insight_value.insight_name = element['name']
                    insight_value.save()
                    page_insight.values.add(insight_value)
            page_insight.save()
            page.insights.add(page_insight)

    ########################################################### get insights pour chaque adaccount facebook ##########################################################
    for adacnt in namesAndAdaccIDs:
        adActId = str(adacnt[1])
        print(adacnt[0])
        print("getting campaigns "+adActId)
        adact = AdAccount(adActId)

        ############################################################################## get campaigns #################################################################################
        
        campaigns = adact.get_campaigns(fields=(AdCampaign.Field.status,AdCampaign.Field.account_id,AdCampaign.Field.id,AdCampaign.Field.name,AdCampaign.Field.objective,
        AdCampaign.Field.start_time,AdCampaign.Field.stop_time,AdCampaign.Field.updated_time,AdCampaign.Field.created_time,AdCampaign.Field.lifetime_budget))

        ############################################################################## get adsets #################################################################################

        # adsets = adact.get_ad_sets(fields=(AdSet.Field.campaign_id,AdSet.Field.account_id,AdSet.Field.id,AdSet.Field.name,AdSet.Field.targeting,AdSet.Field.start_time,AdSet.Field.end_time,AdSet.Field.time_stop
        # ,AdSet.Field.status,AdSet.Field.lifetime_budget,AdSet.Field.optimization_goal))

        ############################################################################## get ads #################################################################################

        ads = adact.get_ads(fields=(Ad.Field.account_id,Ad.Field.campaign_id,Ad.Field.adset_id,Ad.Field.id,Ad.Field.engagement_audience,Ad.Field.created_time,Ad.Field.updated_time,
        Ad.Field.status,Ad.Field.name,Ad.Field.targeting))

        #-----------------------------------------------Saving Campaign------------------------------------------------# 

        adaccount = Ad_Account.objects.get(adaccount_id=adActId)# get the Adaccount where the Id equal to adActId

        for c in ads:
            ad = Ads.objects.filter(ad_id=c["id"])                                          
            if ad.exists():
                pass
            else:
                ad_targeting = Ad_Targeting.objects.create()
                ad_targeting.age_max = c["targeting"]["age_max"] 
                ad_targeting.age_min = c["targeting"]["age_min"]
                if ("genders" in c["targeting"]):
                    ad_targeting.genders = c["targeting"]["genders"] 

                if ("geo_locations" in c["targeting"] ) :
                    if ("countries" in c["targeting"]["geo_locations"]) :
                        ad_targeting.location_countries = c["targeting"]["geo_locations"]["countries"]
                    if ("location_types" in c["targeting"]["geo_locations"]) :
                        ad_targeting.location_types = c["targeting"]["geo_locations"]["location_types"]

                if ("publisher_platforms" in c["targeting"]) : 
                    ad_targeting.publisher_platforms = c["targeting"]["publisher_platforms"]
                    
                if ("facebook_positions" in c["targeting"]):    
                    ad_targeting.facebook_positions = c["targeting"]["facebook_positions"]

                if ("device_platforms" in c["targeting"]):
                    ad_targeting.device_platforms = c["targeting"]["device_platforms"]

                if ("instagram_positions" in c["targeting"]):    
                    ad_targeting.instagram_positions = c["targeting"]["instagram_positions"]
                
                ad,create = Ads.objects.get_or_create(ad_id=c["id"])
                ad.name = c["name"]
                ad.adset_id = c["adset_id"]
                ad.campaign_id = c["campaign_id"]
                ad.account_id = c["account_id"]
                if ("created_time" in c ):
                    ad.created_time = c["created_time"]
                if ("updated_time" in c ):
                    ad.updated_time = c["updated_time"]
                ad.status = c["status"]
                ad_targeting.save()
                ad.targeting = ad_targeting
                ad.save()

        for c in campaigns:
            campaign = Campaign.objects.filter(campaign_id=c["id"])
            if campaign.exists():
                pass
            else:
                campaign = Campaign.objects.create(campaign_id = c["id"])
                campaign.name = c["name"]
                campaign.account_id = c["account_id"]
                campaign.objective = c["objective"]
                if ("start_time" in c ):
                    campaign.start_time = c["start_time"]
                campaign.status = c["status"]
                if ("stop_time" in c ):
                    campaign.stop_time = c["stop_time"]
                if ("updated_time" in c ):
                    campaign.updated_time = c["updated_time"]
                if ('lifetime_budget' in c):
                    campaign.lifetime_budget = c["lifetime_budget"]

                ads = Ads.objects.filter(campaign_id=c["id"])
                for ad in ads:
                    campaign.ads.add(ad)
                campaign.save()
               
        #-----------------------------------------------Saving Campaign------------------------------------------------# 
        print("saving campaigns into adaccount")
        campaigns = Campaign.objects.filter(account_id=adActId)
        print(campaigns)
        for campaign in campaigns:
            adaccount.campaigns.add(campaign)
            adaccount.save()

    return redirect('facebook_auth:home')

#----------------------------------------work with pages----------------------------------------#

@login_required
def get_one_page_insight(request):
    name = request.GET.get('name', '')
    pages = []
    if (len(name)>0):
        pages.append(Account_Page.objects.get(name=name))
    else:
        for page in Account_Page.objects.all():
            pages.append(page)
    cef = User.objects.filter(username =str(request.user))[0]
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret) 
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    me = AdUser(fbid='me')
    for page in pages:
        pageId = page.page_id
        print(page.name)
        access_token = page.access_token
        graphPage = facebook.GraphAPI(access_token=access_token,version="2.9")
        api = API.objects.filter(name="FacebookGraph",provider="Facebook")
        queryset = Metric.objects.filter(API=api[0])
        for metric in queryset:
            e = time.time() #page_tab_views_login_top&since='+s+'&until='+e+"&period=day
            s = time.time()-(90*24*3600) #on retranche le nombe de seconde dans un mois 
            e,s=str(ceil(e)),str(ceil(s))
            returnedAPIData = graphPage.get_connections(id=pageId, connection_name='insights?metric='+metric.queryName+'&since='+s+'&until='+e+'&period=day')
            print(metric.queryName)
            for element in returnedAPIData['data']:
                page_insight,created = Page_Insight.objects.get_or_create(page_insights_id=element['id'])
                page_insight.page_insights_id = element['id']
                page_insight.name = element['name']
                page_insight.period = element['period'] 
                page_insight.title = element['title']
                page_insight.description = element  ['description']
                for value in element['values']:
                    insight_value,created = Insights_Value.objects.get_or_create(insight_name=element['name'],end_time=value['end_time'],insights_value_id=pageId)
                    insight_value.insights_value_id = pageId
                    insight_value.value = str(value['value'])
                    insight_value.end_time = value['end_time']
                    insight_value.insight_name = element['name']
                    insight_value.save()
                    page_insight.values.add(insight_value)
            page_insight.save()
            page.insights.add(page_insight)
    
    for page in pages:
        pageId = page.page_id
        access_token = page.access_token
        posts = Page(pageId).get_posts(fields=[PagePost.Field.actions,PagePost.Field.message,PagePost.Field.message_tags,PagePost.Field.created_time,
        PagePost.Field.is_instagram_eligible,PagePost.Field.comments_mirroring_domain,PagePost.Field.is_hidden,PagePost.Field.is_popular,
        PagePost.Field.shares])
        
        for post in posts:
            # try:
            #     page_post = Post.objects.get(post_id=post["id"])
            # except:
            page_post,created = Post.objects.get_or_create(post_id=post["id"])
            if ("message" in post):
                page_post.message = post["message"]
            if ("message_tags" in post):
                page_post.message_tags = post["message_tags"]
            if ("created_time" in post):
                page_post.created_time = post["created_time"]
            if ("shares" in post):
                page_post.shares = int(post["shares"]["count"])
            if ("is_instagram_eligible" in post):
                page_post.is_instagram_eligible = post["is_instagram_eligible"]
            if ("comments_mirroring_domain" in post):
                page_post.comments_mirroring_domain = post["comments_mirroring_domain"]
            if ("is_hidden" in post):
                page_post.is_hidden = post["is_hidden"]
            if ("is_popular" in post):
                page_post.is_popular = post["is_popular"]
            for action in post["actions"]:
                page_post.link = action["link"]
            page_post.save()
            page.posts.add(page_post)

        page.save() 


    
    return redirect("facebook_auth:synchronous")



#----------------------------------------work with pages----------------------------------------#


@login_required
def get_one_adaccount_insight(request):
    name = request.GET.get('name', '')
    adaccounts = []
    if(len(name)>0):
        try:
            adaccounts.append(Ad_Account.objects.get(name=name))
        except:
            print("mal9ahch")
    else:
        for accnt in Ad_Account.objects.all():
            adaccounts.append(accnt)

    cef = User.objects.filter(username =str(request.user))[0]
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret)
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    for adaccount in adaccounts:
        adActId = adaccount.adaccount_id
        print("getting campaigns inside report view "+adActId)
        adact = AdAccount(adActId)

        ############################################################################## get campaigns #################################################################################
        
        campaigns = adact.get_campaigns(fields=(AdCampaign.Field.status,AdCampaign.Field.account_id,AdCampaign.Field.id,AdCampaign.Field.name,AdCampaign.Field.objective,
        AdCampaign.Field.start_time,AdCampaign.Field.stop_time,AdCampaign.Field.updated_time,AdCampaign.Field.created_time,AdCampaign.Field.lifetime_budget))

        ############################################################################## get adsets #################################################################################

        # adsets = adact.get_ad_sets(fields=(AdSet.Field.campaign_id,AdSet.Field.account_id,AdSet.Field.id,AdSet.Field.name,AdSet.Field.targeting,AdSet.Field.start_time,AdSet.Field.end_time,AdSet.Field.time_stop
        # ,AdSet.Field.status,AdSet.Field.lifetime_budget,AdSet.Field.optimization_goal))

        ############################################################################## get ads #################################################################################

        ads = adact.get_ads(fields=(Ad.Field.account_id,Ad.Field.campaign_id,Ad.Field.adset_id,Ad.Field.id,Ad.Field.engagement_audience,Ad.Field.created_time,Ad.Field.updated_time,
        Ad.Field.status,Ad.Field.name,Ad.Field.targeting))


        #-----------------------------------------------Saving Campaign------------------------------------------------#

        for c in ads:
            ad = Ads.objects.filter(ad_id=c["id"])                                          
            if ad.exists():
                pass
            else:
                ad_targeting = Ad_Targeting.objects.create()
                ad_targeting.age_max = c["targeting"]["age_max"] 
                ad_targeting.age_min = c["targeting"]["age_min"]
                if ("genders" in c["targeting"]):
                    ad_targeting.genders = c["targeting"]["genders"] 

                if ("geo_locations" in c["targeting"] ) :
                    if ("countries" in c["targeting"]["geo_locations"]) :
                        ad_targeting.location_countries = c["targeting"]["geo_locations"]["countries"]
                    if ("location_types" in c["targeting"]["geo_locations"]) :
                        ad_targeting.location_types = c["targeting"]["geo_locations"]["location_types"]

                if ("publisher_platforms" in c["targeting"]) : 
                    ad_targeting.publisher_platforms = c["targeting"]["publisher_platforms"]
                    
                if ("facebook_positions" in c["targeting"]):    
                    ad_targeting.facebook_positions = c["targeting"]["facebook_positions"]

                if ("device_platforms" in c["targeting"]):
                    ad_targeting.device_platforms = c["targeting"]["device_platforms"]

                if ("instagram_positions" in c["targeting"]):    
                    ad_targeting.instagram_positions = c["targeting"]["instagram_positions"]
                
                ad,create = Ads.objects.get_or_create(ad_id=c["id"])
                ad.name = c["name"]
                ad.adset_id = c["adset_id"]
                ad.campaign_id = c["campaign_id"]
                ad.account_id = c["account_id"]
                if ("created_time" in c ):
                    ad.created_time = c["created_time"]
                if ("updated_time" in c ):
                    ad.updated_time = c["updated_time"]
                ad.status = c["status"]
                ad_targeting.save()
                ad.targeting = ad_targeting
                ad.save()

        for c in campaigns:
            campaign = Campaign.objects.filter(campaign_id=c["id"])
            if campaign.exists():
                pass
            else:
                campaign = Campaign.objects.create(campaign_id = c["id"])
                campaign.name = c["name"]
                campaign.account_id = c["account_id"]
                campaign.objective = c["objective"]
                if ("start_time" in c ):
                    campaign.start_time = c["start_time"]
                campaign.status = c["status"]
                if ("stop_time" in c ):
                    campaign.stop_time = c["stop_time"]
                if ("updated_time" in c ):
                    campaign.updated_time = c["updated_time"]
                if ('lifetime_budget' in c):
                    campaign.lifetime_budget = c["lifetime_budget"]

                ads = Ads.objects.filter(campaign_id=c["id"])
                for ad in ads:
                    campaign.ads.add(ad)
                campaign.save()
               
        #-----------------------------------------------Saving Campaign------------------------------------------------# 
        print("saving campaigns into adaccount")
        campaigns = Campaign.objects.filter(account_id=adActId)
        for campaign in campaigns:
            adaccount.campaigns.add(campaign)
            adaccount.save()

        return redirect("facebook_auth:synchronous")



def campaign_detail(request):
    name = request.GET.get('name', '')
    adaccounts = []
    if(len(name)>0):
        adaccounts.append(Ad_Account.objects.get(name=name))
    else:
        for accnt in Ad_Account.objects.all():
            adaccounts.append(accnt)
    ads = []        
    for adaccount in adaccounts:  
        print(adaccount.name)  
        last_date = str(adaccount.last_update)
        campaigns = Campaign.objects.filter(account_id=adaccount.id)
        for campaign in campaigns :
            start_time = campaign.start_time
            start_time = start_time.split("T",1)[0]
            start_time = start_time[2:]
            start_time = reversed(start_time.split("-",2))
            start_time = '/'.join(start_time)
            print(start_time)
            print(len(start_time))
            print("raouf"+last_date)
            first_date = datetime.datetime.strptime(last_date,"%d/%m/%y")
            second_date = datetime.datetime.strptime(start_time,'%d/%m/%y')
            if (first_date < second_date):
                for ad in campaign.ads.all():
                    ads.append([ad,campaign])
            else:
                break
        last_date = datetime.date.today()
        last_date = last_date - datetime.timedelta(days=30)
        print("boussa :"+ str(last_date))
        last_date = str(last_date.strftime("%d/%m/%y"))
        adaccount.last_update = last_date
    cef = User.objects.filter(username =str(request.user))[0]
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret)
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    e = datetime.date.today()
    first = e.replace(day=1)
    s = first - datetime.timedelta(days=1) #on retranche le nombre de seconde dans un mois
    e = str(e)
    s = str(s)
    # e,s=str(ceil(e)),str(ceil(s))
    print(e)
    print(s)
    params = {
    'time_increment':1,  ## this is to say we will have 1 result per day by defualt value is all-day which means one value for whole time rant
    'time_range': {  ## time range in by default for the last month - unix timestamps are not supported
        'since': s,#str(today - datetime.timedelta(days=24)),
        'until': e,#"2018-08-28",
    },
    'fields': [AdsInsights.Field.clicks,AdsInsights.Field.cpc,AdsInsights.Field.cpp,AdsInsights.Field.cpm,AdsInsights.Field.ctr,AdsInsights.Field.impressions
    ,AdsInsights.Field.date_start,AdsInsights.Field.date_stop,AdsInsights.Field.spend,AdsInsights.Field.frequency,AdsInsights.Field.engagement_rate_ranking,
    AdsInsights.Field.reach,AdsInsights.Field.cost_per_action_type,AdsInsights.Field.conversion_rate_ranking,AdsInsights.Field.cost_per_thruplay
    ],
    }
    for ad,campaign in ads:
        print("dkhel")
        id = ad.ad_id
        ad_insights = Ad_Insight.objects.filter(ad_id=id)
        if (ad_insights.exists()):
            ad_insights.delete()
        insights = Ad(id).get_insights(params=params)
        for element in insights:
            ad_insight = Ad_Insight.objects.create(ad_id=id)
            ad_insight.clicks = element["clicks"]
            ad_insight.conversion_rate_ranking = element["conversion_rate_ranking"]
            if ("cpc" in element):
                ad_insight.cpc = element["cpc"]
            ad_insight.cpm = element["cpm"]
            ad_insight.cpp = element["cpp"]
            ad_insight.ctr =  element["ctr"]
            ad_insight.date_start = element["date_start"]
            ad_insight.date_stop = element["date_stop"]
            ad_insight.engagement_rate_ranking = element["engagement_rate_ranking"]
            ad_insight.frequency = element["frequency"]
            ad_insight.impressions =element["impressions"]
            ad_insight.reach = element["reach"]
            ad_insight.spend = element["spend"]
            if ("cost_per_action_type" in element):
                for action in element["cost_per_action_type"] :
                    cost_per_action_type,created = Cost_Per_Action_Type.objects.get_or_create(cost_per_action_type_id = (ad.ad_id+"/"+action["action_type"]+"/"+action ["value"]))
                    cost_per_action_type.action_type = action["action_type"]
                    cost_per_action_type.value = action ["value"]
                    cost_per_action_type.save()
                    ad_insight.cost_per_action_type.add(cost_per_action_type)
            
            if ("cost_per_thruplay" in element):
                for action in element["cost_per_thruplay"] :
                    cost_per_thruplay,created = Cost_Per_Thruplay.objects.get_or_create(cost_per_thruplay_id = (ad.ad_id+"/"+action["action_type"]+"/"+action ["value"]))
                    cost_per_thruplay.action_type = action["action_type"]
                    cost_per_thruplay.value = action["value"]
                    cost_per_thruplay.save()
                    ad_insight.cost_per_thruplay.add(cost_per_thruplay)
            ad_insight.save()
            ad = Ads.objects.get(ad_id=id)
            ad.insights.add(ad_insight)
            ad.save()
    return redirect("facebook_auth:synchronous")

def getJSON(file_path):
    with open(file_path,'r',encoding="utf-8-sig") as f:
        data = f.read()
        print(type(data))
        objects = JSON.loads(data)
        return objects



def compare_campaign(camp1,camp2):
    if(camp1.niche==camp2.niche and camp1.location_types==camp2.location_types and camp1.citie==camp2.citie
        and camp1.region==camp2.region and camp1.device_platforms==camp2.device_platforms and
        camp1.publisher_platforms==camp2.publisher_platforms and camp1.positions==camp2.positions):
        return True
    else:
        return False

def verify_not_exist_befor(ad,tab):
    try:
        for obj in tab:
            for camp,count in obj:
                if (ad.id == camp.id):
                    return False
        return True
    except :
        return True
    


def campaigns_experience(request):
    # module_dir = os.path.dirname(__file__)  # get current directory
    # file_path = os.path.join(module_dir, 'bdd.json')
    # objects = getJSON(file_path)

    # for obj in objects["campaigns"]:
    #     campaign,created = Experience_Campaign.objects.get_or_create(id = obj["id"])
    #     campaign.name = obj["name"]
    #     campaign.objective = obj["objective"]
    #     campaign.niche = obj["niche"]
    #     campaign.age_max = obj["age_max"]
    #     campaign.age_min = obj["age_min"]
    #     campaign.genders = obj["genders"]
    #     campaign.created_time = obj["created_time"]
    #     campaign.cpc = obj["cpc"]
    #     campaign.cpm = obj["cpm"]
    #     campaign.cpp = obj["cpp"]
    #     campaign.clicks = obj["clicks"]
    #     campaign.frequency = obj["frequency"]
    #     campaign.ctr = obj["ctr"]
    #     campaign.location_types = obj["location_types"]
    #     campaign.country = obj["country"]
    #     campaign.citie = obj["citie"]
    #     campaign.region = obj["region"]
    #     campaign.device_platforms = obj["device_platforms"]
    #     campaign.publisher_platforms = obj["publisher_platforms"]
    #     campaign.positions = obj["positions"]
    #     campaign.save()


    utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
    utilisateur.save()
    qs = Experience_Campaign.objects.all()
    regions_table = []
    objectivs_table = []
    domains_table = []
    devices_table = []
    genders_table = []
    publisher_platforms_table = []
    positions_table = []
    country_table = []
    for obj in qs:
        if (obj.citie in regions_table):
            pass
        else:
            regions_table.append(obj.citie)  
        if (obj.objective in objectivs_table):
            pass
        else:
            objectivs_table.append(obj.objective)
        if (obj.niche in domains_table):
            pass
        else:
            domains_table.append(obj.niche)
        if (obj.device_platforms in devices_table):
            pass
        else:
            devices_table.append(obj.device_platforms)
        if (obj.genders in genders_table):
            pass
        else:
            genders_table.append(obj.genders)
        if (obj.publisher_platforms in publisher_platforms_table):
            pass
        else:
            publisher_platforms_table.append(obj.publisher_platforms)
        if (obj.positions in positions_table):
            pass
        else:
            positions_table.append(obj.positions)
        if (obj.country in country_table):
            pass
        else:
            country_table.append(obj.country)
    if request.method == 'POST':
        form = Experience_Campain(request.POST)
        if (form.is_valid()):
            objective = request.POST['Objective']
            niche = request.POST['Domain']
            genders = request.POST['Gender']
            method_filter = request.POST['filter']
            # citie = request.POST['Places']
            # country = request.POST['Country']
            # device_platforms = request.POST['Devices']
            # publisher_platforms = request.POST['platforms']
            # positions = request.POST['Positions']
            qs = Experience_Campaign.objects.filter(objective=objective,niche=niche,genders = genders).order_by('efficiency').reverse()#,niche=niche,genders=genders,citie=citie)    
            #device_platforms=device_platforms,publisher_platforms=publisher_platforms,positions=positions)
            campaigns = qs[:8]
            if (len(qs)>1):
                data = True
                tb = []
                print("raouf")
                print(method_filter)
                for camp in qs:
                    tb_compare = []
                    count = 0
                    if (verify_not_exist_befor(camp,tb)):
                        for ad in qs:
                            if (compare_campaign(camp,ad)):
                                count = count + 1
                                tb_compare.append((ad,count))
                        tb.append(tb_compare)

                result = []
                for obj in tb:
                    cpc = 0
                    cpp = 0
                    cpm = 0
                    ctr = 0
                    efficiency = 0
                    for ad,count in obj:
                        cpc = cpc + float(ad.cpc)
                        cpp = cpp + float(ad.cpp)
                        cpm = cpm + float(ad.cpm)
                        ctr = ctr + float(ad.ctr)
                        efficiency = efficiency + ad.efficiency
                    cpc = cpc/len(obj)
                    cpp = cpp/len(obj)
                    cpm = cpm/len(obj)
                    ctr = ctr/len(obj)
                    efficiency = efficiency/len(obj)
                    for ob,count in obj:
                        ads = ob
                        counts = count
                    result.append((ads,cpc,cpp,cpm,ctr,efficiency,counts))
                
                
                # qs1 = Experience_Campaign.objects.filter(region=objective)
                # qs3 = Experience_Campaign.objects.filter(region=niche)
                # qs4 = Experience_Campaign.objects.filter(region=places)
                # qs5 = Experience_Campaign.objects.filter(region=genders)
                # qs6 = Experience_Campaign.objects.filter(region=device_platforms)
                # qs7 = Experience_Campaign.objects.filter(region=publisher_platforms)
                # qs8 = Experience_Campaign.objects.filter(region=positions)
                return render(request,"campaign_experience.html",locals())
            else:
                data = False
                return render(request,"campaign_experience.html",locals())
    return render(request,"campaign_experience.html",locals())


class Campaign_Ads_Insights(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, *args, **kwargs):
        ad_Id = kwargs["ad_Id"]
        ad = Ads.objects.filter(ad_id=ad_Id)[0]
        insights = ad.insights.all()

        ads_insight_context = {
        "insight_cpc" : "",
        "insight_cpm" : "",
        "insight_ctr" : "",
        "insight_impressions" : "",
        "insight_reach" : "",
        "insight_cpp" : "",
        "insight_dates" : "",
        "insight_clicks" : "",
        "insight_frequency" : "",
        "insight_spend" : "",
        "insight_engagement_rate_ranking" : "",
        "insight_conversion_rate_ranking" : "",
        }

        insight_cpc = []
        insight_cpm = []
        insight_ctr = []
        insight_impressions = []
        insight_reach = []
        insight_cpp = []
        insight_clicks = []
        insight_frequency = []
        insight_spend = []
        insight_engagement_rate_ranking = []
        insight_conversion_rate_ranking = []
        insight_dates = []
        
        for insight in insights: 
            insight_cpc.append(insight.cpc)
            insight_cpm.append(insight.cpm)
            insight_ctr.append(insight.ctr)
            insight_impressions.append(insight.impressions)
            insight_reach.append(insight.reach)
            insight_cpp.append(insight.cpp)
            insight_dates.append(insight.date_start)
            insight_clicks.append(insight.clicks)
            insight_frequency.append(insight.frequency)
            insight_spend.append(insight.spend)
            insight_engagement_rate_ranking.append(insight.engagement_rate_ranking)
            insight_conversion_rate_ranking.append(insight.conversion_rate_ranking)


        ads_insight_context.update({
        "insight_cpc" : insight_cpc,
        "insight_cpm" : insight_cpm,
        "insight_ctr" : insight_ctr,
        "insight_impressions" : insight_impressions,
        "insight_reach" : insight_reach,
        "insight_cpp" : insight_cpp,
        "insight_dates" : insight_dates,
        "insight_clicks" : insight_clicks,
        "insight_frequency" : insight_frequency,
        "insight_spend" : insight_spend,
        "insight_engagement_rate_ranking" : insight_engagement_rate_ranking,
        "insight_conversion_rate_ranking" : insight_conversion_rate_ranking,

        })

        return Response(ads_insight_context)

class Page_Fans(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        insights = page.insights.filter(name="page_fans")[0]

        page_fans_context = {
            "labels":insights.name,
            "insight_value":"",
            "insight_date":"",
        }

        insight_date = []
        insight_value = []
        values = insights.values.all()
        for value in values: 
            insight_value.append(value.value)
            end_time = ''
            for i in range(0,10):                        #get the first part of the string date ex: yyyy/mm/dd 
                end_time = end_time + value.end_time[i]  #
            insight_date.append(end_time)
        page_fans_context.update({
            "insight_value":insight_value,
            "insight_date":insight_date,
        })

        return Response(page_fans_context)


class Page_Metric_Choice(APIView): #view donne les statistique d'une metric choisit dans le dashboard page insight
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        metric = kwargs["metric"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        insights = page.insights.filter(name=metric)[0]

        context = {
            "labels":insights.name,
            "insight_value":"",
            "insight_date":"",
        }

        insight_date = []
        insight_value = []
        values = insights.values.all()
        for value in values: 
            insight_value.append(value.value)
            end_time = ''
            for i in range(0,10):                        #get the first part of the string date ex: yyyy/mm/dd 
                end_time = end_time + value.end_time[i]  #
            insight_date.append(end_time)
        context.update({
            "insight_value":insight_value,
            "insight_date":insight_date,
        })

        return Response(context)


class Page_View_Logged_Logout(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        insight_logout = page.insights.filter(name="page_views_logout")[0]
        insight_logged_in = page.insights.filter(name="page_views_logged_in_total")[0]


        page_view_logged_context = {
            "labels":insight_logged_in.name,
            "insight_value":"",
            "insight_date":"",
        }
        page_view_logout_context = {
            "labels":insight_logout.name,
            "insight_value":"",
            "insight_date":"",
        }


        insight_date = []
        insight_value = []
        values = insight_logged_in.values.all()
        for value in values: 
            insight_value.append(value.value)
            end_time = ''
            for i in range(0,10):                        #get the first part of the string date ex: yyyy/mm/dd 
                end_time = end_time + value.end_time[i]  #
            insight_date.append(end_time)
        page_view_logged_context.update({
            "insight_value":insight_value,
            "insight_date":insight_date,
        })
        
        insight_date_b = []
        insight_value_b = []
        values_b = insight_logout.values.all()
        for value in values_b: 
            insight_value_b.append(value.value)
            end_time = ''
            for i in range(0,10):                        #get the first part of the string date ex: yyyy/mm/dd 
                end_time = end_time + value.end_time[i]  #
            insight_date_b.append(end_time)
        page_view_logout_context.update({
            "insight_value":insight_value_b,
            "insight_date":insight_date_b,
        })

        result = {
            "page_views_logout":page_view_logout_context,
            "page_views_logged_in_total":page_view_logged_context,
        }

        return Response(result)


class Page_Impressions(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        qs = page.insights.all()
        

        page_impressions_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }

        page_post_impressions_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }

        page_impressions_paid_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }
        page_impressions_organic_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }
        for insight in qs:
            if((insight.name == "page_impressions_paid") or (insight.name == "page_impressions_organic") or (insight.name == "page_impressions") or (insight.name == "page_posts_impressions")):
                insight_date = []
                insight_value = []
                values = insight.values.all()
                for value in values: 
                    insight_value.append(value.value)
                    end_time = ''
                    for i in range(0,10):
                        end_time = end_time + value.end_time[i]
                    insight_date.append(end_time)
                if(insight.name == "page_impressions_paid"):
                    page_impressions_paid_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })
                elif (insight.name == "page_impressions_organic"):
                    page_impressions_organic_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })
                elif (insight.name == "page_impressions"):
                    page_impressions_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })
                elif (insight.name == "page_posts_impressions"):
                    page_post_impressions_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })    
        result = {
        "page_impressions_paid":page_impressions_paid_context,
        "page_impressions_organic":page_impressions_organic_context,
        "page_posts_impressions" : page_post_impressions_context,
        "page_impressions" : page_impressions_context,
        }
        return Response(result)


class Page_Posts_Impressions(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        qs = page.insights.all()

        page_posts_impressions_organic_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }
        page_posts_impressions_paid_context = {
            "labels":"",
            "insight_value":"",
            "insight_date":"",
        }
        for insight in qs:
            if((insight.name == "page_posts_impressions_organic") or (insight.name == "page_posts_impressions_paid")):
                insight_date = []
                insight_value = []
                values = insight.values.all()
                for value in values: 
                    insight_value.append(value.value)
                    end_time = ''
                    for i in range(0,10):
                        end_time = end_time + value.end_time[i]
                    insight_date.append(end_time)
                if(insight.name == "page_posts_impressions_paid"):
                    page_posts_impressions_paid_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })
                elif (insight.name == "page_posts_impressions_organic"):
                    page_posts_impressions_organic_context.update({
                        "labels":insight.name,
                        "insight_value":insight_value,
                        "insight_date":insight_date,
                    })
        result = {
        "page_posts_impressions_paid":page_posts_impressions_paid_context,
        "page_posts_impressions_organic":page_posts_impressions_organic_context
        }
        return Response(result)

class Page_Fans_City(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        insights = page.insights.filter(name="page_fans_city")[0]
        page_fans_city = {
            "labels":"page_fans_city",
            "insight_value":"",
            "insight_date":"",
        }

        insight_date = []
        insight_value = []
        values = insights.values.all()
        for value in values: 
            insight_value.append(value.value)
            end_time = ''
            for i in range(0,10):
                end_time = end_time + value.end_time[i]
            insight_date.append(end_time)
        page_fans_city.update({
            "insight_value":insight_value,
            "insight_date":insight_date,
        })
        return Response(page_fans_city)


class Page_Negative_Feedback(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        pageId = kwargs["pageId"]
        page = Account_Page.objects.filter(page_id=pageId)[0]
        insights = page.insights.filter(name="page_negative_feedback")[0]
        page_negative_feedback = {
            "labels":"page_negative_feedback",
            "insight_value":"",
            "insight_date":"",
        }

        insight_date = []
        insight_value = []
        values = insights.values.all()
        for value in values: 
            insight_value.append(value.value)
            end_time = ''
            for i in range(0,10):
                end_time = end_time + value.end_time[i]
            insight_date.append(end_time)
        page_negative_feedback.update({
            "insight_value":insight_value,
            "insight_date":insight_date,
        })
        return Response(page_negative_feedback)


def home(request):
    pageId = request.GET.get('pageId', '') # cas facebook page graph
    access_token = request.GET.get('access_token','') #access token of the page with id (pageID)
    adActId = request.GET.get('adActId', '') # cas facebook ads

    if len(pageId)>0:
        return HttpResponseRedirect("/home/page?pageId="+pageId)
    elif len(adActId)>0:
        return HttpResponseRedirect("/home/adaccount?adActId="+adActId)
    else:
        pages = Account_Page.objects.all()
        adacnts = Ad_Account.objects.all()
        adaccounts = []
        for adacnt in adacnts:
            if (adacnt.name != "Raouf Boussa" and adacnt.name != "bm-pub"):
                adaccounts.append(adacnt)
        utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
        utilisateur.save()

        return render(request,"account_home.html",locals())

@login_required
def dashbaord_page(request):
    pageId = request.GET.get('pageId', '')
    if (len(pageId)>0):
        try:
            page = Account_Page.objects.filter(page_id=pageId)[0]
            userprofile,created = UserProfile.objects.get_or_create(user = request.user)
            userprofile.save()
            api = API.objects.filter(name="FacebookGraph",provider="Facebook")
            qs = Metric.objects.filter(API=api[0])
            metrics = []
            for metric in qs:
                if (metric.queryName != "page_negative_feedback" and metric.queryName != "page_fans" and metric.queryName != "page_impressions_paid" and metric.queryName != "page_impressions_organic" and metric.queryName != "page_posts_impressions_paid" and metric.queryName != "page_posts_impressions_organic" and metric.queryName != "	page_fans_city" and metric.queryName != "page_views_logout" and metric.queryName != "page_views_logged_in_total" and metric.queryName != "page_fans_gender_age" and metric.queryName != "	page_fans_online" and metric.queryName != "page_fans_online_per_day" and metric.queryName != "page_fan_adds_by_paid_non_paid_unique" and metric.queryName != "page_fans_locale" and metric.queryName != "page_fans_country" and metric.queryName != "page_actions_post_reactions_anger_total" and metric.queryName != "page_actions_post_reactions_sorry_total" and metric.queryName != "page_actions_post_reactions_haha_total" and metric.queryName != "page_actions_post_reactions_wow_total" and metric.queryName != "page_actions_post_reactions_like_total" and metric.queryName != "page_actions_post_reactions_love_total "):
                    metrics.append(metric)
            context = {
                'page_objects' : page,
                'metrics' : metrics,
                'utilisateur' : userprofile,
                'cover_page': page.cover,
                'insights' : page.insights,
            }
            return render(request,'index.html',context)
        except ObjectDoesNotExist:
            messages.warning(request, "page ID n'exist pas dans l'url")
            return redirect("/")
    else:
        return redirect("facebook_auth:home")
   

    
@login_required
def dashbaord_adaccount(request):
    adActId = request.GET.get('adActId', '')
    if (len(adActId)>0):
        try:
            adaccount = Ad_Account.objects.get(adaccount_id=adActId)
            campaigns = Campaign.objects.filter(account_id=adaccount.id)
            ads = []
            print(campaigns)
            for campaign in campaigns :
                start_time = campaign.start_time
                start_time = start_time.split("T",1)[0]
                start_time = start_time[2:]
                start_time = reversed(start_time.split("-",2))
                start_time = '/'.join(start_time)
                print(start_time)
                print(len(start_time))
                first_date = datetime.datetime.strptime("25/04/20","%d/%m/%y")
                second_date = datetime.datetime.strptime(start_time,'%d/%m/%y')
                if (first_date < second_date):
                    for ad in campaign.ads.all():
                        ads.append([ad,campaign])
                else:
                    break
            # cef = User.objects.filter(username =str(request.user))[0]
            # my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
            # my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
            # my_app_id = str(my_social_app.client_id)
            # my_app_secret = str(my_social_app.secret)
            # FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
            # e = datetime.date.today()
            # first = e.replace(day=1)
            # s = first - datetime.timedelta(days=1) #on retranche le nombe de seconde dans un mois
            # e = str(e)
            # s = str(s)
            # # e,s=str(ceil(e)),str(ceil(s))
            # print(e)
            # print(s)
            # params = {
            # 'time_increment':1,  ## this is to say we will have 1 result per day by defualt value is all-day which means one value for whole time rant
            # 'time_range': {  ## time range in by default for the last month - unix timestamps are not supported
            #     'since': s,#str(today - datetime.timedelta(days=24)),
            #     'until': e,#"2018-08-28",
            # },
            # 'fields': [AdsInsights.Field.clicks,AdsInsights.Field.cpc,AdsInsights.Field.cpp,AdsInsights.Field.cpm,AdsInsights.Field.ctr,AdsInsights.Field.impressions
            # ,AdsInsights.Field.date_start,AdsInsights.Field.date_stop,AdsInsights.Field.spend,AdsInsights.Field.frequency,AdsInsights.Field.engagement_rate_ranking,
            # AdsInsights.Field.reach,AdsInsights.Field.cost_per_action_type,AdsInsights.Field.conversion_rate_ranking,AdsInsights.Field.cost_per_thruplay
            # ],
            # }
            # for ad,campaign in ads:
            #     id = ad.ad_id
            #     ad_insights = Ad_Insight.objects.filter(ad_id=id)
            #     if (ad_insights.exists()):
            #         ad_insights.delete()
            #     insights = Ad(id).get_insights(params=params)
            #     for element in insights:
            #         ad_insight = Ad_Insight.objects.create(ad_id=id)
            #         ad_insight.clicks = element["clicks"]
            #         ad_insight.conversion_rate_ranking = element["conversion_rate_ranking"]
            #         if ("cpc" in element):
            #             ad_insight.cpc = element["cpc"]
            #         ad_insight.cpm = element["cpm"]
            #         ad_insight.cpp = element["cpp"]
            #         ad_insight.ctr =  element["ctr"]
            #         ad_insight.date_start = element["date_start"]
            #         ad_insight.date_stop = element["date_stop"]
            #         ad_insight.engagement_rate_ranking = element["engagement_rate_ranking"]
            #         ad_insight.frequency = element["frequency"]
            #         ad_insight.impressions =element["impressions"]
            #         ad_insight.reach = element["reach"]
            #         ad_insight.spend = element["spend"]
            #         if ("cost_per_action_type" in element):
            #             for action in element["cost_per_action_type"] :
            #                 cost_per_action_type,created = Cost_Per_Action_Type.objects.get_or_create(cost_per_action_type_id = (ad.ad_id+"/"+action["action_type"]+"/"+action ["value"]))
            #                 cost_per_action_type.action_type = action["action_type"]
            #                 cost_per_action_type.value = action ["value"]
            #                 cost_per_action_type.save()
            #                 ad_insight.cost_per_action_type.add(cost_per_action_type)
                    
            #         if ("cost_per_thruplay" in element):
            #             for action in element["cost_per_thruplay"] :
            #                 cost_per_thruplay,created = Cost_Per_Thruplay.objects.get_or_create(cost_per_thruplay_id = (ad.ad_id+"/"+action["action_type"]+"/"+action ["value"]))
            #                 cost_per_thruplay.action_type = action["action_type"]
            #                 cost_per_thruplay.value = action["value"]
            #                 cost_per_thruplay.save()
            #                 ad_insight.cost_per_thruplay.add(cost_per_thruplay)
            #         ad_insight.save()
            #         ad = Ads.objects.get(ad_id=id)
            #         ad.insights.add(ad_insight)
            #         ad.save()
            start_date = adaccount.created_time
            start_date = start_date[:10]
            userprofile,created = UserProfile.objects.get_or_create(user = request.user)
            userprofile.save()
            context = {
                'adaccount_objects' : adaccount,
                'adsets' : ads,
                'utilisateur' : userprofile,
                'insights' : adaccount.insights,
                'start_date' : start_date,
            }
            return render(request,'index2.html', context)
        except ObjectDoesNotExist:
            messages.warning(request, "adAccount ID n'exist pas dans l'url")
            return redirect("/")
    else:
        return redirect("facebook_auth:home")


def synchronous_data(request):
    # adActId = request.GET.get('adActId', '')
    pages = Account_Page.objects.all()
    ad_account = Ad_Account.objects.all()
    userprofile,created = UserProfile.objects.get_or_create(user = request.user)
    userprofile.save()
    adaccounts = []
    for adacnt in ad_account:
        if (adacnt.name != "Raouf Boussa" and adacnt.name != "bm-pub"):
            adaccounts.append(adacnt)
    context = {
                'pages' : pages,
                'ad_account' : adaccounts,
                'utilisateur' : userprofile,
            }
    return render(request,'synchronous_data.html', context)
    



    

@login_required
def dashbaord_V3(request):
    utilisateur,created = UserProfile.objects.get_or_create(user = request.user)
    utilisateur.save()
    return render(request,'index3.html', locals())



@login_required
def data_table(request):

    return render(request,'Campaigns_table.html', locals())



def upload_pic(request):
    pageId = request.GET.get('pageId','')
    adacnt = request.GET.get('adacnt','')
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user = UserProfile.objects.get(user = request.user)
            user.avatar = form.cleaned_data['image']
            user.save()
            # messages.SUCCESS(request,"image uploaded seccessfuly")
            if (len(pageId)>0):
                return redirect('/home/page?pageId=' + pageId)
            else:
                if (len(adacnt)>0):
                    return redirect('/home/adaccount?pageId=' + pageId)
                else:
                    return redirect('/home')
    return render(request,'upload_img.html', locals())


def delete_all(request):
    camps = Experience_Campaign.objects.all()
    for camp in camps:
        efficiency = 1/float(camp.cpc)+1/float(camp.cpm)+float(camp.cpp)+float(camp.ctr)+int(camp.frequency)
        camp.efficiency = efficiency
        camp.save()
    # Ad_Targeting.objects.all().delete()
    # Post.objects.all().delete()
    # Ads.objects.all().delete()
    # Page_Insight.objects.all().delete()
    # Insights_Value.objects.all().delete()
    # Action.objects.all().delete()
    # Account_Page.objects.all().delete()
    # Ad_Account_Insight.objects.all().delete()
    # Ad_Account.objects.all().delete()
    # Campaign.objects.all().delete()
    # Cost_Per_Action_Type.objects.all().delete()
    # Cost_Per_Outbound_Click.objects.all().delete()
    # Cost_Per_Thruplay.objects.all().delete()
    # Cost_Per_Unique_Action_Type.objects.all().delete()
    # Cost_Per_Unique_Outbound_Click.objects.all().delete()
    # Cover_Photo.objects.all().delete()
    # Attribution_Spec.objects.all().delete()
    # return redirect("facebook_auth:getdata")
    return HttpResponse("success")