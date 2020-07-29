import httplib2
from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import (
    SocialAccount,
    SocialApp,
    SocialToken
    )
import facebook,json
# from facebookads.api import FacebookAdsApi
from django.views.generic import ListView
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.campaign import Campaign
from facebookads.adobjects.adaccountuser import AdAccountUser as AdacUser
from facebookads.adobjects.campaign import Campaign
from django.http import HttpResponse
import time,datetime
from math import ceil
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from googleads import adwords
from googleads import oauth2
from datetime import datetime


from facebookads.adobjects.adsinsights import AdsInsights
import re
from random import randrange
from django.http import HttpResponseRedirect
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials


def chaouki(request):
    JSONFormatedAPIDATA = json.dumps({'username':'chaouki','data de naissance':'12-6-1985'}, indent =3)
    return HttpResponse(JSONFormatedAPIDATA)

def prepareReport(request):
    pageId = request.GET.get('pageId', '') # cas facebook page graph
    adActId = request.GET.get('adActId', '') # cas facebook ads
    if len(pageId+adActId)>0: # il a déjà choisi sur quoi il faut faire le rapport
        return HttpResponseRedirect("/report?pageId="+pageId+"&adActId="+adActId)
    else:
        cef = User.objects.filter(username =str(request.user))[0]
        my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
        my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
        my_app_id = str(my_social_app.client_id)
        my_app_secret = str(my_social_app.secret) 
        FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
        me = AdUser(fbid='me')
        accounts = me.get_pages(fields=[Page.Field.name,Page.Field.id,Page.Field.new_like_count,
        # Page.Field.access_token,Page.Field.category,Page.Field.fan_count,Page.Field.is_owned,
        # Page.Field.name_with_location_descriptor,Page.Field.network,Page.Field.offer_eligible,
        # Page.Field.page_token,Page.Field.cover,Page.Field.about,
        # Page.Field.parent_page,Page.Field.parking,Page.Field.payment_options,
        # Page.Field.personal_info,Page.Field.personal_interests,Page.Field.whatsapp_number,
        # Page.Field.were_here_count,Page.Field.website,Page.Field.voip_info,
        # Page.Field.verification_status,Page.Field.username,Page.Field.unseen_message_count,
        # Page.Field.unread_notif_count,Page.Field.unread_message_count,Page.Field.talking_about_count,
        # Page.Field.supports_instant_articles,Page.Field.studio,Page.Field.store_number,
        # Page.Field.store_location_descriptor,Page.Field.store_code,Page.Field.schedule
        ])
        adAccounts = me.get_ad_accounts(fields=[AdAccount.Field.name,AdAccount.Field.id,
        # AdAccount.Field.account_id,AdAccount.Field.account_status,
        # AdAccount.Field.ad_account_creation_request,
        # AdAccount.Field.ad_account_promotable_objects,
        # AdAccount.Field.age,AdAccount.Field.agency_client_declaration,
        # AdAccount.Field.amount_spent,AdAccount.Field.attribution_spec,AdAccount.Field.balance,AdAccount.Field.business,  ######## proprietées pour l'admin de l'entreprise
        # AdAccount.Field.business_city,AdAccount.Field.business_country_code,AdAccount.Field.business_name,               ######## must be business admin of your Business Manager to call this API
        # AdAccount.Field.business_state,AdAccount.Field.business_street,AdAccount.Field.business_street2,
        # AdAccount.Field.business_zip,AdAccount.Field.can_create_brand_lift_study,AdAccount.Field.capabilities
        ])
        namesAndIDs = []
        namesAndAccIds = []
        for account in accounts:
            namesAndIDs.append((account['name'],account['id']))
        for adAcc in adAccounts:
            namesAndAccIds.append((adAcc['name'],adAcc['id']))
        return render(request,'prepareReport.html', locals())


def chooseAccount(request):
    cef = User.objects.filter(username =str(request.user))[0]
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    #print(token[0].token)
    #accounts = graph.get_connections(id='me', connection_name='accounts')
    accounts = graph.get_all_connections(id='me', connection_name='accounts')
    namesAndIDs = []
    for account in accounts:
        #print("generateur get_all_connections  ", account ,"\n\n")
        namesAndIDs.append((account['name'],account['id'],account['access_token']))

    #Iterates over all pages returned by a get_connections call and yields the individual items
    #namesAndIDs= [ (account['name'],account['id'],account['access_token']) for account in accounts['data']]
    pageId = request.GET.get('pageId', '0')
    adActId = request.GET.get('adActId', '0')
    print("accounts ", accounts,"names and Ids", namesAndIDs)
    # try:
    #     if int(pageId)>0 and int(adActId[4:])>0 :
    #         print("pageid et adActId sont là, tout va buenoooo\n    ")
    #         print(pageId,adActId)
    # except ValueError:
    #     adActId = 9999 # if adActId == 9999 means no adActId
    #
    #pageId,pageToken = accounts['data'][2]['id'],accounts['data'][2]['access_token']

    # if(3>5):
    #     return HttpResponseRedirect("/path/")

    if int(pageId)>0:
        return HttpResponseRedirect("/test?pageId="+pageId+"&adActId="+adActId)
    return render(request,'chooseAccount.html', locals())

def findTokenFromPageId(accounts,pageId):
    for acc in accounts:
        print("inside find token ", pageId , acc['id'])
        if pageId == acc['id']:
            print("\nfound the page Id in accounts")
            return acc['access_token']
    print("\ndidn't find pageid in accounts")
    return ""

def getFacebookData(request):
    if request.user.is_authenticated:
            token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook')
            graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
            accounts = graph.get_connections(id='me', connection_name='accounts')
            pageId,pageToken = accounts['data'][0]['id'],accounts['data'][0]['access_token']
            graphPage = facebook.GraphAPI(access_token=pageToken,version="3.0")
            e = time.time()
            s = time.time()-(31*24*3600) #on retranche le nombe de seconde dans un mois
            e,s=str(ceil(e)),str(ceil(s))
            print(e,s)

            returnedAPIData = graphPage.get_connections(id=pageId, connection_name='insights?metric=page_impressions&since='+s+'&until='+e+"&period=day")
            JSONFormatedAPIDATA = json.dumps(returnedAPIData, indent =3)
    else:
        JSONFormatedAPIDATA = json.dumps([ {"post": {"id" :"eee"}}
        ])
    return HttpResponse(JSONFormatedAPIDATA)

def facebookInsightsViews(request):
    userName = request.GET.get('username', '')
    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username =userName)[0]
    print("retrieved user from react's GET request ", cef)
    s = request.GET.get('start', '') #startDate
    e = request.GET.get('end', '') #end Date
    metric = request.GET.get('metric', '') #metric type

    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    accounts = graph.get_connections(id='me', connection_name='accounts')
    print('accounts : \n\n')
    print(accounts)
    pageId = request.GET.get('pageId','')# accounts['data'][2]['id'])
    adActId = request.GET.get('adActId', '0')
    pageToken = findTokenFromPageId(accounts['data'],pageId)
    #pageId,pageToken = accounts['data'][2]['id'],accounts['data'][2]['access_token']
    pageToken = pageToken if pageToken else accounts['data'][2]['access_token']
    graphPage = facebook.GraphAPI(access_token=pageToken,version="3.0")
    print("url cef ", 'insights?metric='+metric+'&since='+s+'&until='+e+"&period=day")
    returnedAPIData = graphPage.get_connections(id=pageId, connection_name='insights?metric='+metric+'&since='+s+'&until='+e+"&period=day")
    # fanCount = graphPage.get_object(id=pageId, fields='fan_count')
    # returnedAPIData['likes (fan count)'] = fanCount
    JSONFormatedAPIDATA = json.dumps(returnedAPIData, indent =3)

    #page_views_total The number of times a Page's profile has been viewed by logged in and logged out people.
    #page_impressions impressions of all the page content : post, ads, checkins ...
    #page_post_engagements   engagement of all post
    #page_video_views of at least 3s excluding replays
    #page_video_views_10s  of at least 10s excluding replays
    #
    # field for number of likes in fan_count fanCount = graphPage.get_object(id=pageToQuery[0], fields='fan_count')
    return HttpResponse(JSONFormatedAPIDATA)

def facebookOneNumberMetric(request):
    metric = request.GET.get('metric', '') #startDate
    userName = request.GET.get('username', '')

    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username = userName)[0]
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    accounts = graph.get_connections(id='me', connection_name='accounts')
    pageId = accounts['data'][2]['id']
    pageToken = accounts['data'][2]['access_token']
    # pageId = request.GET.get('pageId','')
    # pageToken = findTokenFromPageId(accounts['data'],pageId)
    graphPage = facebook.GraphAPI(access_token=pageToken,version="3.0")
    fanCount = graphPage.get_object(id=pageId, fields=metric)
    JSONFormatedAPIDATA = json.dumps(fanCount, indent =3)

    return HttpResponse(JSONFormatedAPIDATA)

def facebookOneNumberMetric_test(request):
    metric = request.GET.get('metric', '') #startDate
    userName = request.GET.get('username', '')

    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username = userName).first()
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook').first())
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret) 
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    me = AdacUser('me')
    accounts = me.get_pages(fields=[Page.Field.name,Page.Field.id])
    #pageId = accounts['data'][2]['id']
    #pageToken = accounts['data'][2]['access_token']
    pageId = request.GET.get('pageId','')
    pageToken = findTokenFromPageId(accounts['data'],pageId)
    graphPage = facebook.GraphAPI(access_token=pageToken,version="3.0")
    fanCount = graphPage.get_object(id=pageId, fields=metric)
    JSONFormatedAPIDATA = json.dumps(fanCount, indent =3)

    return HttpResponse(JSONFormatedAPIDATA)

def facebookAdsRelevanceScores(request):
    userName = request.GET.get('username', '')
    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username =userName)[0]
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    my_app_id = '217964325484293'
    my_app_secret = '9594c58c2d895491856ccfda5852955a'
    my_access_token = str(token[0])
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    adAccounts = graph.get_connections(id='me', connection_name='adaccounts')
    account = AdAccount('act_1075170155957258')#LG  ('act_500815316726081') #gen42
    camps = account.get_campaigns()
    startDate = request.GET.get('start', '') #startDate
    endDate = request.GET.get('end', '') #end Date
    params = {
    #    'time_increment':1,  ## this is to say we will have 1 result per day by defualt value is all-day which means one value for whole time rant
        'time_range': {  ## time range in by default for the last month - unix timestamps are not supported
            'since': startDate,#str(today - datetime.timedelta(days=24)),
            'until': endDate,#"2018-08-28",
        },
        'fields': [
            'relevance_score', ## relevance_score works only on the ad level not campaign or adset level
            'ad_name'
        ],
    }
    ads = camps[0].get_ads()
    relevanceScores = []
    for i in range(len(ads)):
        adsInsights = ads[i].get_insights(params=params)
        print(adsInsights)
        relevanceScores.append(adsInsights)  #ad level to see relevance_score
    labelAndValues = [{"label":x[0]['ad_name'],'value':x[0]['relevance_score']['score']} for x in relevanceScores]
    print(relevanceScores)
    print(labelAndValues)
    return HttpResponse(json.dumps(labelAndValues))

from ourUtils.sqlite3Utils import insertAdInDB
from facebookads.adobjects.adcreative import AdCreative
import time
def facebookAdsBodyAndScore(request):
    #http://localhost:8000/facebookAdsBodyAndScore?username=moncef to query and change act_id to get campaigns of desired account
    userName = request.GET.get('username', '')
    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username =userName)[0]
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    my_app_id = '217964325484293'
    my_app_secret = '9594c58c2d895491856ccfda5852955a'
    my_access_token = str(token[0])
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    adAccounts = graph.get_connections(id='me', connection_name='adaccounts')
    #print(adAccounts)
    adAccIds= []
    for adAcc in adAccounts['data']:
        adAccIds.append(adAcc['id'])
    adAccIdsManual= ['act_873372226137053', 'act_883320418475567', 'act_879846302156312', 'act_851303915010551', 'act_866528316821444', 'act_869963726477903', 'act_863446320462977', 'act_915119641962311', 'act_988610641279877', 'act_988611174613157', 'act_1025635340910740', 'act_1015433918597549', 'act_994465150694426', 'act_1024008024406805', 'act_1009875819153359', 'act_1026260820848192', 'act_1057048464436094', 'act_1029802250494049', 'act_1040140746126866', 'act_1060421924098748', 'act_1045516675589273', 'act_453659671730078', 'act_1085547938252813', 'act_316798405521839', 'act_1081011315373142', 'act_237256413699466', 'act_1075170155957258', 'act_1531641910273576', 'act_288948314983410', 'act_354456271750201', 'act_498816030540594', 'act_177961156237785', 'act_464596047368504']
    adAccIds += adAccIdsManual
    print("il y a ", len(adAccIds), " adAcc et ils sont  : ",adAccIds)
    params = {'fields': ['relevance_score'],
               'date_preset': 'lifetime',
               'filtering':[{'field':'impressions','operator':'GREATER_THAN_OR_EQUAL','value':'500'}]

               }
    paramsAds = {'filtering':[{'field':'relevance_score','operator':'GREATER_THAN_OR_EQUAL','value':'0'}]} # on filtre pour avoir que ceux qui ont un relevanceScore}
    adsNameAndBody = {}
    k = 0
    for  j,adId in enumerate(adAccIds[1:]):#de 1 car 0 déjà traitée
        try:
            #account = AdAccount('act_1075170155957258')
            account = AdAccount(adId)
            myAds= account.get_ads()#params=paramsAds)
            print("il y a  : ",len(myAds)," ads dans l'acc id ", j)
            for myAd in myAds:
                print("ad ", k)
                k+=1
                try:
                    creative = myAd.get_ad_creatives()[0]
                    myAdInsights = myAd.get_insights(params=params)
                    if len(myAdInsights)>0:# des fois y a pas d'insights
                        myCreative = creative.remote_read(fields=[AdCreative.Field.name, AdCreative.Field.body])
                        adName,adBody,adScore= myCreative[AdCreative.Field.name],myCreative[AdCreative.Field.body],myAdInsights[0]["relevance_score"]["score"]
                        adsNameAndBody[adName]={"indice":0,"body":adBody,"relevance_score":adScore}
                        insertAdInDB(adName,adBody,adScore)
                    else:
                        print("ad sans insights donc rien écrit à notre DB")
                except Exception as e:
                    print("exception in ads loop",type(e), e)
                    # time.sleep(60)
                    # print("3 min to go")
                #
                    if not isinstance(e, KeyError): # keyerror c'est erreur ou il manque un field (key in dico), et donc si c pas ça c limit reached donc o nattend
                        time.sleep(60)
                        print("4 min to go")
                        time.sleep(60)
                        print("3 min to go")
                        time.sleep(60)
                        print("2 min to go")
                        time.sleep(60)
                        print("1 min to go")
                        time.sleep(60)
                    continue
            # camps = account.get_campaigns()
            # print("il y a  : ",len(camps)," campagnes dans l'acc id ", j)
            # print(camps)
            #camps  = camps[:len(camps)//2]
            #camps  = camps[1:2]
            #camps  = camps[len(camps)//2:]
            #added 03/01
        # for i,c in enumerate(camps) :
        #         try:
        #             print("ad account" ,j , " campaingn ", i , " ",c)
        #             myAds = c.get_ads()
        #             if len(myAds)<1:
        #                 print("no ads in campaign")
        #             for myAd in myAds:
        #                 try:
        #                     creative = myAd.get_ad_creatives()[0]
        #                     myCreative = creative.remote_read(fields=[AdCreative.Field.name, AdCreative.Field.body])
        #                     myAdInsights = myAd.get_insights(params=params)
        #                     if len(myAdInsights)>0:# des fois y a pas d'insights
        #                         adName,adBody,adScore= myCreative[AdCreative.Field.name],myCreative[AdCreative.Field.body],myAdInsights[0]["relevance_score"]["score"]
        #                         adsNameAndBody[adName]={"indice":i,"body":adBody,"relevance_score":adScore}
        #                         insertAdInDB(adName,adBody,adScore)
        #                     else:
        #                         print("ad sans text donc rien écrit à notre DB")
        #                 except:
        #                     time.sleep(60)
        #                     print("2 min to go")
        #                     time.sleep(60)
        #                     print("1 min to go")
        #                     time.sleep(60)
        #                     continue
        #         except:
        #             time.sleep(60)
        #             print("2 min to go")
        #             time.sleep(60)
        #             print("1 min to go")
        #             time.sleep(60)
        #             continue
        except Exception as e:
                print("limit in ad acc. Exception : " , e)
                #time.sleep(60)
                print("2 min to go")
                time.sleep(60)
                print("1 min to go")
                time.sleep(60)
                continue

    #end added 03/
    result = json.dumps(adsNameAndBody, indent=2)
    # with open('ads.json', 'a+') as outfile:
    #     json.dump(result, outfile)
    return HttpResponse(result)
from django.views.decorators.csrf import csrf_exempt
from pseudoAPI.models import Report

from pseudoAPI.models import API

@csrf_exempt
def saveReport(request):
    print(type(request.user),request.user)
    l = [e for e in request.POST.items()]
    state = l[0][0]
    print(state)
    parsedState = json.loads(state)
    print("state reçu " ,parsedState)
    if len(str(parsedState['reportId'])) > 0:#update d'un rapport existant
        r = Report.objects.filter(user=request.user,id =parsedState['reportId']).update(report=state,name=parsedState['reportTitle'])
        return HttpResponse("Rapport mis à jour")
    else:#création new rapport
        r = Report(report = "" , user = request.user,name=parsedState['reportTitle'],API=API.objects.get(name=parsedState['API']))
        r.save()
        parsedState['reportId'] = r.id
        r.report = json.dumps(parsedState)
        r.save()
        return HttpResponse(json.dumps({"id":r.id}))

from django.core.mail import send_mail
from email.mime.image  import MIMEImage
from email.mime.application import MIMEApplication
from django.core.mail import EmailMessage
import base64
#receive png from client, parse it and then send it
@csrf_exempt
def sendEmail(request):
    post = [e for e in request.POST.items()]
    print("post send email before json parse ",post, post[0][1],post[1][1])
    format, imgstr = post[0][1].split(';base64,')
    emailAddress = post[1][1]
    email = EmailMessage(
    'Rapport 42',
    'Merci de trouver ci-joint votre rapport.',
    'from@example.com',
    [emailAddress],
    reply_to=['another@example.com'],
    headers={'Message-ID': 'foo'},
    )
    email.attach('rapport.png', base64.b64decode(imgstr), 'image/png')
    email.send(fail_silently=False)
    return HttpResponse("email sent")
@csrf_exempt
def sendEmailPhantom(request):#send mail from report generated by phantomjs
    file_name = downloadWithPhantom(request)
    emailAddress = request.GET.get('email', '')
    # post = [e for e in request.POST.items()]
    # print("POST received ",post)
    # format, imgstr = post[0][1].split(';base64,')
    # emailAddress = post[0][1]
    # reportId = post[0][1]
    email = EmailMessage(
    'Rapport 42',
    'Merci de trouver ci-joint votre rapport.',
    'from@example.com',
    [emailAddress],
    reply_to=['another@example.com'],
    headers={'Message-ID': 'foo'},
    )
    #email.attach('rapport.png', base64.b64decode(imgstr), 'image/png')
    email.attach_file(file_name)
    email.send(fail_silently=False)
    return HttpResponse("email sent")
@csrf_exempt
def sendEmailReportCommand(periodicId):#,username,reportId,emailAddress): # encapsulate download behavior in this function so it can be reused elsewhere without httpreponse (in sendMail for instance)
    periodicReport= PeriodicReport.objects.filter(id=periodicId)[0]
    emailAddress = periodicReport.emailAddress
    user = periodicReport.report.user
    username = user.username
    reportId = str(periodicReport.report.id)
    print(emailAddress,user,username,reportId)
    #user = User.objects.filter(username=username)[0]
    logoImagepath = './assets/'+str(Logo.objects.filter(user =user)[0].logo)
    logoBase64= 'data:image/png;base64,'
    import base64
    with open(logoImagepath, "rb") as image_file:
        logoBase64 += str(base64.b64encode(image_file.read()))[2:-1]
    file_name = "./assets/reports/djangoReport_"+username+str(int(time.time()))+".pdf"
    print("downloading report for ",)
    url ="http://localhost:8000/report?reportId="+reportId+'&username='+username+"&phantomjs=1"+"&periodicId="+str(periodicId)# 'http://' + request.get_host() + '/downloadReport'
    external_process = Popen(["./phantomjs/phantomjs", './phantomjs/convertpdf.js', url, file_name,logoBase64],
                                 stdout=PIPE, stderr=STDOUT)
    external_process.wait()
    email = EmailMessage(
    'Rapport 42',
    'Merci de trouver ci-joint votre rapport.',
    'from@example.com',
    [emailAddress],
    reply_to=['another@example.com'],
    headers={'Message-ID': 'foo'},
    )
    #email.attach('rapport.png', base64.b64decode(imgstr), 'image/png')
    email.attach_file(file_name)
    email.send(fail_silently=False)

@csrf_exempt
def updateReport(request):
    r = Report()

def loadReport(request):
    reportId = request.GET.get('reportId', '')
    if len(reportId)>0:
        #r = Report.objects.filter(user=request.user,id =reportId)[0]
        #for phantomjs
        r = Report.objects.filter(id =reportId)[0]
        r = r.report
        r = json.loads(r)
        #print("loaded report ", r['gridElements'], "time", str(int(time.time())))
        periodicId = request.GET.get('periodicId', '')
        if periodicId !='-1': #il s'agit d'un périodique, il faut changer la date
            periodicReport= PeriodicReport.objects.filter(id=periodicId)[0]
            periodInDays = periodicReport.periodInDays
            for e in r['gridElements']:
                e['endDate'] = int(time.time())
                e['startDate'] = int(time.time())-periodInDays*3600*24

        return   HttpResponse(json.dumps(r))
    else:
        return HttpResponse("Error during report load")

from django.views.generic import CreateView, UpdateView
from pseudoAPI.models import Logo,PeriodicReport
class LogoCreate(CreateView):
    model = Logo
    fields = ['logo']
    template_name = 'LogoCreate.html'
    success_url = '/reportList'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(LogoCreate, self).form_valid(form)
from django.shortcuts import get_object_or_404
class LogoUpdate(UpdateView):
    model = Logo
    fields = ['logo']
    template_name = 'LogoCreate.html'
    success_url = '/reportList'
    def get_object(self, queryset=None):
        return get_object_or_404(Logo, user =self.request.user)
from FacebookOAuth.forms import PeriodicCreateForm
class PeriodicReportCreate(CreateView):
    def get_form_kwargs(self): # on envoie le current user comme parametre pour filtrer les reports et prendre que les siens
        kwargs = super(PeriodicReportCreate,self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    form_class = PeriodicCreateForm
    # model = PeriodicReport
    # fields = ['name','report','periodInDays','nextRunDate','emailAddress']
    template_name = 'PeriodicReportCreate.html'
    success_url = '/reportList'


from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT
from django.views.generic import TemplateView, View
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.core.files.base import ContentFile
from django.http import FileResponse
import time
def downloadReport(request):
    file_name = downloadWithPhantom(request)
    return HttpResponse(file_name)
def downloadWithPhantom(request): # encapsulate download behavior in this function so it can be reused elsewhere without httpreponse (in sendMail for instance)
    logoImagepath = './assets/'+str(Logo.objects.filter(user =request.user)[0].logo)
    logoBase64= 'data:image/png;base64,'
    import base64
    with open(logoImagepath, "rb") as image_file:
        logoBase64 += str(base64.b64encode(image_file.read()))[2:-1]
    #file = open("./phantomjs/base64Img.txt")
    #logoBase64  = file.read()
    #print(logoBase64)
    reportId = request.GET.get('reportId', '')
    username = str(request.user)
    file_name = "./assets/reports/djangoReport_"+username+str(int(time.time()))+".pdf"
    print("downloading report for ",)
    url ="http://" + request.get_host() + "/report?reportId="+reportId+'&username='+username+"&phantomjs=1"# 'http://' + request.get_host() + '/downloadReport'
    external_process = Popen(["./phantomjs/phantomjs", './phantomjs/convertpdf.js', url, file_name,logoBase64],
                                 stdout=PIPE, stderr=STDOUT)
    external_process.wait()
    return file_name



from django.views.generic.list import ListView
class ReportList(ListView):
    model = Report
    context_object_name = "reports"
    template_name = "reportList.html"
    paginate_by = 5
    def get_queryset(self):
       return Report.objects.filter(user=self.request.user , id__gte=1)
    # def get_context_data(self, **kwargs):
    #     # Nous récupérons le contexte depuis la super-classe
    #     context = super(reportList, self).get_context_data(**kwargs)
    #     # Nous ajoutons la liste des catégories, sans filtre particulier
    #     #context['reports'] = Report.objects.filter(user=self.request.user)
    #     return context



def facebookAds(request):
    userName = request.GET.get('username', '')
    print("the username is"+userName)
    if len(userName)>0:
        print("dynamic user fetched from react'request GET param :", userName)
    else:
        print("couldn't fetch from react'request GET param, default to empty string ")
        userName=""
    cef = User.objects.filter(username =userName)[0]
    token = SocialToken.objects.filter(account__user=cef, account__provider='facebook')
    graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
    my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
    my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
    my_app_id = str(my_social_app.client_id)
    my_app_secret = str(my_social_app.secret) 
    FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    adActId = request.GET.get('adActId', '')
    if len(adActId)<5 :
        raise Exception("**Ad Account non fourni par la requête.**")
    account = AdAccount(adActId)#'act_1075170155957258')#LG  ('act_500815316726081') #gen42
    campaignId = request.GET.get('campaign', '')
    if len(campaignId)<5 :
        raise Exception("**Campagne non fourni par la requête.**")
    campaign = Campaign(campaignId)
    print('della3')
    print(campaign)
    # users = account.get_users()
    # result = {'adAccount' : adAccounts }
    # result['users'] = users
    # result['account'] = account
    #print("Ads : \n\n\n")
    # compaignNames = []
    # camps = account.get_campaigns(fields=["name"]) #adding fields options here and giving a list does the same as the remote read
    # print("ayayaya*********" , camps ,"*********")
    # # oneCamp = Campaign("6099547558377") # get one campaign by id (so we can present multiple campaigns to user then let him choose)
    # # print("camps" , oneCamp)
    # for c in camps[:4]:
    #     print(" c camps[name]" , c._data)
        # campaign = c.remote_read(fields=[Campaign.Field.name])
        # compaignNames.append(campaign[Campaign.Field.name])
    #someCampaignInsights = account.get_campaigns()[0].get_insights(fields=[AdsInsights.Field.spend,AdsInsights.Field.cpc]) // one compaign

    ### this loop just to get the same camp from camps equal to oneCamp but only the former works when fetching Insights
    # j = 0
    # while oneCamp['id']!= camps[j]['id']:
    #     j= j + 1

    #today = datetime.date.today()
    startDate = request.GET.get('start', '') #startDate
    endDate = request.GET.get('end', '') #end Date
    metric = request.GET.get('metric', '')
    print("raouftest"+metric)
    params = {
    'time_increment':1,  ## this is to say we will have 1 result per day by defualt value is all-day which means one value for whole time rant
    'time_range': {  ## time range in by default for the last month - unix timestamps are not supported
        'since': startDate,#str(today - datetime.timedelta(days=24)),
        'until': endDate,#"2018-08-28",
    },
    'fields': [ metric #AdsInsights.Field.truc = 'truc'  ycha9iw fina bark
        # 'spend',#AdsInsights.Field.spend,
        # 'cpc',#AdsInsights.Field.cpc,
        # 'cpm',#AdsInsights.Field.cpm,
        # 'impressions',#AdsInsights.Field.impressions,
        # 'reach',#AdsInsights.Field.reach,
        # #AdsInsights.Field.impressions,
        # 'inline_post_engagement',#AdsInsights.Field.inline_post_engagement, ### inline_post_engagement is attributed if action(app instaltion) happens within 1 day after click on ad
        # 'video_10_sec_watched_actions',#AdsInsights.Field.video_10_sec_watched_actions ## il y a 10s, 30s ou bien des pourcentages 100%, 25% .....
        # 'relevance_score', ## relevance_score works only on the ad level not campaign or adset level
    ],
    }

    #someCampaignInsights = camps[1].get_ads()[0].get_insights(params=params)  #ad level to see relevance_score
    someCampaignInsights = campaign.get_insights(params=params)  # compaign level

    # print("one camp ", oneCamp['id'])
    # print("get compaigns: ", camps)
    # print("compare: ", oneCamp['id'] == camps[1]['id'] ) ## the same camapign (not same instance) but one fails with insights the other doesn't ???? init ??
    #adsInsights = someCampaignInsights[0]
    #insight = someCampaignInsights.remote_read(fields=[AdsInsights.Field.spend])

    #print("the name of retrieved compaign insights: " ,camps[1].remote_read(fields=[Campaign.Field.name]) )
    #print(result)
    # print("campaign Names \n")
    # print(compaignNames)
    print("les campaigns li djebnaha:")#ou d'un ad :")
    print(someCampaignInsights)
    #print(adsInsights)
    #print(insight[AdsInsights.Field.spend])

    #print("ad accounts)",adAccounts)
    #print()
    #JSONFormatedAPIDATA = json.dumps({"data":str(someCampaignInsights)}, indent=2)

    def mon_generateur():
        i = 0
        while True:
            i = i + 1
            yield i
    mon_iterateur = iter(mon_generateur())

    def my_replace(m):
        return '"item' +str(next(mon_iterateur)) +'":' #+str(randrange(50)) +'":'

    result = re.sub("<AdsInsights>", my_replace, str(someCampaignInsights)) #. #replace("",'"item":')

    result  = list(result)
    result[0] = "{"
    result[-1] = "}"
    "".join(result)
    print("result " ,"".join(result))
    return HttpResponse(result)

###### Abdelhak test code --- google analytics ---

def metricIsAnInt(metric):
    return  metric in ('ga:users', 'ga:newUsers', 'ga:pageviews')


def metricIsFloat(metric):
    return metric in ('ga:pageviewsPerSession', 'ga:bounceRate')


def googleAnalyticsNumber(request):
    metric = request.GET.get('metric', '')
    startDate = request.GET.get('start', '')  # startDate
    endDate = request.GET.get('end', '')  # end Date



    DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
    VIEW_ID = '103592216'
    abdelhak = User.objects.filter(username='abdelhak')[0]
    token = SocialToken.objects.filter(account__user=abdelhak, account__provider='google')
    token = token[0].token
    credentials = AccessTokenCredentials(token,'Google API for Python')
    http = httplib2.Http()
    http = credentials.authorize(http)
#    credentials = google.oauth2.credentials.Credentials(token)
    #authed_http = AuthorizedHttp(credentials)
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
    response = analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
         # 'dimensions': [{'name': 'ga:date'}],
          'metrics': [{'expression': metric}]
        }]
      }
    ).execute()


    response_data = response.get('reports',[])[0]
    if (metricIsAnInt(metric)):
        metric_value = int(response_data.get('data',{}).get('rows',[])[0].get('metrics',[])[0].get('values',[])[0])

    elif(metricIsFloat(metric)):
        metric_value = round(float(response_data.get('data', {}).get('rows', [])[0].get('metrics', [])[0].get('values', [])[0]),2)

    else:
        metric_value = response_data.get('data',{}).get('rows',[])[0].get('metrics',[])[0].get('values',[])[0]

    print('metric value', metric_value)
    metric_dic = {metric: metric_value}
    JSONFormatedAPIDATA = json.dumps(metric_dic, indent=3)

    return HttpResponse(JSONFormatedAPIDATA)

    #printing data
    # parsed_data = parse_response(response_data)[0]
    # print(parsed_data) #dataFrame
    # # for report in response.get('reports', []):
    #     columnHeader = report.get('columnHeader', {})
    #     dimensionHeaders = columnHeader.get('dimensions', [])
    #     metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    #     rows = report.get('data', {}).get('rows', [])
    #
    #     for row in rows:
    #         dimensions = row.get('dimensions', [])
    #         dateRangeValues = row.get('metrics', [])
    #
    #         for header, dimension in zip(dimensionHeaders, dimensions):
    #             print('in headers and dimensions')
    #             print(header + ': ' + dimension)
    #
    #         for i, values in enumerate(dateRangeValues):
    #             print ('Date range (' + str(i) + ')')
    #             for metricHeader, value in zip(metricHeaders, values.get('values')):
    #                 print('in metrics and values')
    #                 print (metricHeader.get('name') + ': ' + value)

def googleAnalyticsWithDimensions(request):
    metric = request.GET.get('metric', '')
    startDate = request.GET.get('start', '')  # startDate
    endDate = request.GET.get('end', '')  # end Date
    dim = request.GET.get('dim','')


    DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
    VIEW_ID = '103592216'

    print('got here:')

    abdelhak = User.objects.filter(username='abdelhak')[0]

    token = SocialToken.objects.filter(account__user=abdelhak, account__provider='google')
    print(token)

    token = token[0].token
    credentials = AccessTokenCredentials(token,'Google API for Python')
    http = httplib2.Http()
    http = credentials.authorize(http)
    analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
    response = analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
          'dimensions': [{'name': dim}],
          'metrics': [{'expression': metric}]
        }]
      }
    ).execute()


    response_data = response.get('reports',[])[0]
    returned_data = parse_line_data(response_data)
    JSONFormatedAPIDATA = json.dumps(returned_data, indent= 3)
    return HttpResponse(JSONFormatedAPIDATA)

def parse_line_data(report):

    """Parses and prints the Analytics Reporting API V4 response"""
    #Initialize results, in list format because two dataframes might return
    result_list = []

    #Initialize empty data container for the two dateranges (if there are two that is)
    metrics_data = []
    dimensions_data = []

    #Initialize header rows
    header_row = []

    #Get column headers, metric headers, and dimension headers.
    columnHeader = report.get('columnHeader', {})
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    dimensionHeaders = columnHeader.get('dimensions', [])

    #Combine all of those headers into the header_row, which is in a list format
    for dheader in dimensionHeaders:
        header_row.append(dheader)
    for mheader in metricHeaders:
        header_row.append(mheader['name'])

    #Get data from each of the rows, and append them into a list
    rows = report.get('data', {}).get('rows', [])
    for row in rows:
        row_temp = []
        dimensions = row.get('dimensions', [])
        metrics = row.get('metrics', [])
        for d in dimensions:
            dimensions_data.append(d)
        for m in metrics[0]['values']:

            metrics_data.append(m)

    total = report.get('data', {}).get('totals',[])[0].get('values',{})[0]
    print(total)

    #Putting those list formats into pandas dataframe, and append them into the final result

    result_object = {
        'metrics': metrics_data,
        'dimensions': dimensions_data,
        'total':    total
    }
    return result_object

def googleAdsWithDimensions(request):
    abdelhak = User.objects.filter(username='abdelhak')[0]

    token = SocialToken.objects.filter(account__user=abdelhak, account__provider='google')
    token = token[0].token
    # credentials = AccessTokenCredentials(token,'Google API for Python')
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    startDate = request.GET.get('start', '')
    endDate = request.GET.get('end', '')
    metric = request.GET.get('metric', '')
    print('start and end dates are: ', startDate, endDate)
    client_customer_id = "227-188-3391"  # LG Electronics Algeria
    user_agent = 'Google API for Python'
    developer_token = 'C9npOKuEjmma0aTphIKdmg'
    token_expiry = datetime(2020, 1, 1, 12)
    oauth2_client = oauth2.GoogleAccessTokenClient(token, token_expiry)

    adwords_client = adwords.AdWordsClient(
        developer_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id)

    customer = adwords_client.GetService('CustomerService').getCustomers()[0]

    report_downloader = adwords_client.GetReportDownloader(version='v201809')
    # Create report definition.
    # report = {
    #     'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
    #     'dateRangeType': 'LAST_7_DAYS',
    #     'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
    #     'downloadFormat': 'CSV',
    #     'selector': {
    #         'fields': [metric, 'Date'],
    #         'ordering': ['Date']
    #     }
    # }
    # Create report query.
    report_query = (adwords.ReportQueryBuilder()
                    .Select(metric, 'Date')
                    .From('ACCOUNT_PERFORMANCE_REPORT')
                    .During(start_date=startDate, end_date=endDate)
                    .Build())

    returned_data = report_downloader.DownloadReportAsStringWithAwql(
        report_query,'CSV', skip_report_header=True, skip_column_header=True,
        skip_report_summary=True, include_zero_impressions=True)



    dates = []
    data = []
    unsortedData = []
    for match in re.split(r"\n+", returned_data):
        if match:
            pair = match.split(",")
            #dates.append(pair[1])
            #data.append(pair[0])
            unsortedData.append([pair[1],pair[0]])

    sortedDataByDate = sorted(unsortedData, key= lambda row: datetime.strptime(row[0],"%Y-%m-%d"))

    for pair in sortedDataByDate:
        dates.append(pair[0])
        data.append(pair[1])

    #print("the returned result from google ads api is: ", returned_data)
    #    credentials = google.oauth2.credentials.Credentials(token)
    # authed_http = AuthorizedHttp(credentials)
    # http = httplib2.Http()
    # http = credentials.authorize(http)

    JSONFormatedAPIDATA = json.dumps({'dates': dates, 'metrics': data}, indent=3)
    return HttpResponse(JSONFormatedAPIDATA)



def googleAdsNumber(request):
    abdelhak = User.objects.filter(username='abdelhak')[0]

    token = SocialToken.objects.filter(account__user=abdelhak, account__provider='google')
    token = token[0].token
    # credentials = AccessTokenCredentials(token,'Google API for Python')
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    startDate = request.GET.get('start','')
    endDate = request.GET.get('end','')
    metric = request.GET.get('metric','')

    client_customer_id = "227-188-3391" # LG Electronics Algeria
    user_agent = 'Google API for Python'
    developer_token = 'C9npOKuEjmma0aTphIKdmg'
    token_expiry = datetime(2019, 1, 1, 12)
    oauth2_client = oauth2.GoogleAccessTokenClient(token, token_expiry)

    adwords_client = adwords.AdWordsClient(
        developer_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id)

    customer = adwords_client.GetService('CustomerService').getCustomers()[0]
    returned_data =  get_performance_metric(adwords_client, metric, startDate,endDate)

    print("the returned result from google ads api is: ", returned_data)
    #    credentials = google.oauth2.credentials.Credentials(token)
    #authed_http = AuthorizedHttp(credentials)
    # http = httplib2.Http()
    # http = credentials.authorize(http)

    JSONFormatedAPIDATA = json.dumps({metric: returned_data}, indent=3)
    return HttpResponse(JSONFormatedAPIDATA)


def get_performance_metric(adwords_client, metric,startDate,endDate):
    # Initialize appropriate service.
    report_downloader = adwords_client.GetReportDownloader(version='v201809')

    # Create report query.
    report_query = (adwords.ReportQueryBuilder()
                    .Select(metric)
                    .From('ACCOUNT_PERFORMANCE_REPORT')
                    .During(start_date = startDate,end_date = endDate)
                    .Build())

    result = report_downloader.DownloadReportAsStringWithAwql(
        report_query, 'CSV', skip_report_header=True, skip_column_header=True,
        skip_report_summary=True, include_zero_impressions=False)
    return result





def moncef_test(request):
    abdelhak = User.objects.filter(username='moncef')[0]

    token = SocialToken.objects.filter(account__user=abdelhak, account__provider='google')
    token = token[0].token
    # credentials = AccessTokenCredentials(token,'Google API for Python')
    # http = httplib2.Http()
    # http = credentials.authorize(http)

    client_customer_id = "227-188-3391"  # LG Electronics Algeria
    #client_customer_id =  '242-160-6701'
    user_agent = 'Google API for Python'
    developer_token = 'C9npOKuEjmma0aTphIKdmg'
    token_expiry = datetime(2020, 1, 1, 12)
    oauth2_client = oauth2.GoogleAccessTokenClient(token, token_expiry)

    adwords_client = adwords.AdWordsClient(
        developer_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id)

    customer = adwords_client.GetService('CustomerService').getCustomers()[0]

    report_downloader = adwords_client.GetReportDownloader(version='v201809')



    # this is where u can customize ur request (change date, returned attributres...)
    # https://developers.google.com/adwords/api/docs/appendix/reports/keywords-performance-report
    print()
    report_query = (adwords.ReportQueryBuilder()
                    .Select('Criteria', 'QualityScore')
                    .Where('QualityScore').GreaterThanOrEqualTo(0)
                    .From('KEYWORDS_PERFORMANCE_REPORT')
                    .Where('IsNegative').In('True','False')
                    #.During('LAST_MONTH')
                    .Build())

    returned_data = report_downloader.DownloadReportAsStringWithAwql(
        report_query, 'CSV', skip_report_header=True, skip_column_header=True,
        skip_report_summary=True, include_zero_impressions=True)

    print(returned_data)

    return render(request,'keywords.html', locals())
