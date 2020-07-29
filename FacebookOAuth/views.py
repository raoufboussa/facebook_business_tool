from django.shortcuts import render
from django.http import HttpResponse
from FacebookOAuth.forms import MyTestForm
import requests
from allauth.socialaccount.models import (
    SocialAccount,
    SocialApp,
    SocialToken
    )
import facebook,json
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenCredentials
import pandas
from googleads import adwords
from googleads import oauth2

from facebookads.api import FacebookAdsApi
# from facebookads import adobjects
# from facebookads.adobjects.adaccountuser import AdAccountUser
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.campaign import Campaign

from django.http import HttpResponse
import time,datetime
from math import ceil
# Create your views here.
from django.contrib.auth.models import User


def login(request):
    return render(request,'account/account_set_password.html')

def report(request):
    #print("host ",request.get_host())
    phantomjs = request.GET.get('phantomjs', '0')
    periodicId = request.GET.get('periodicId', '-1')
    print("phantomjs ",phantomjs)
    if phantomjs=="1" or request.user.is_authenticated :
        reportId = request.GET.get('reportId', '') # on veut charger un rapport sauvegardé
        username = request.GET.get('username', '')
        user = ''
        if len(username)>0: #download case
            user = User.objects.filter(username=username)[0]
        else:
            user = request.user
        print("username : ",user.username)
        #token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook')
        token = SocialToken.objects.filter(account__user=user, account__provider='facebook')
        graph = facebook.GraphAPI(access_token=token, version="2.9")#"2.7")
        accounts = graph.get_connections(id='me', connection_name='accounts')
        pageId,pageToken = accounts['data'][0]['id'],accounts['data'][0]['access_token'] # date[2] to data[0] by abdelahk
        graphPage = facebook.GraphAPI(access_token=pageToken,version="2.9")
        pageId = request.GET.get('pageId', '')
        adActId = request.GET.get('adActId', '')
        campaigns = []
        if(len(adActId)>0): # get campaigns if there an ad account
            print("getting campaigns inside report view")
            cef = User.objects.filter(username =str(request.user))[0]
            my_access_token = str(SocialToken.objects.filter(account__user=cef, account__provider='facebook')[0])
            my_social_app = SocialApp.objects.filter(provider='facebook',name="FacebookApp")[0]
            my_app_id = str(my_social_app.client_id)
            my_app_secret = str(my_social_app.secret) 
            FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
            account = AdAccount(adActId)
            compaignNames = []
            camps = account.get_campaigns(fields=["name"])
            campaigns = [{"name":c._data['name'],"id" :c._data['id']} for c in camps]
        #send metrics
        from pseudoAPI.models import Metric,API,Report,Logo
        #choose to which API do the  metrics belong :
        metricsAPI  = ""
        metrics = ""

        if len(reportId)==0: #on trouve l'API en fonction de quel ID on a reçu
            if len(pageId)>0 :
                metricsAPI = 'FacebookGraph'
            elif len(adActId)>0:
                metricsAPI='FacebookAds'
            API_obj = API.objects.get(name=metricsAPI) # on recupere l'objet de l'API voulue
        else:#rapport existant, on connait l'API
            API_obj = Report.objects.get(id=reportId).API
            metricsAPI = API_obj.name
        metrics = [{"name":e.name + " - " +e.API.name,"queryName": e.queryName} for e in Metric.objects.filter(API=API_obj)]
        logoBase64 = '0'
        if phantomjs == '1': # on envoie le logo en base64 s'il s'agit de phantomjs car pour l'avoir dans le header il faut qu'il soit dans la page (probleme de phnatomjs)
            logoImagepath = './assets/'+str(Logo.objects.filter(user =user)[0].logo) # on récupere le logo du user récupérer dans le parametre GET
            logoBase64= 'data:image/png;base64,'
            import base64
            with open(logoImagepath, "rb") as image_file:
                logoBase64 += str(base64.b64encode(image_file.read()))[2:-1]

        props = json.dumps({
        'API' : metricsAPI,
        'pageId' : pageId,
        'adActId' : adActId,
        'campaigns' : campaigns if(len(adActId)>0) else '',
        'username': user.username,## rajouter l'info ou un token du user pour pouvoir reconnaitre quel user après quand on fait une http query de react
        'metrics' : metrics,
        'reportId' : reportId,
        'domain' : request.get_host(),#'localhost:8000'#'limitless-falls-38818.herokuapp.com'
        'phantomjs':phantomjs,
        'base64Img':logoBase64,
        'periodicId' :periodicId,
        })

    return render(request,'reactTest.html', locals())





def profile(request):


    profilConnection,profilFields,pageAccount,pageConnection,pageFields,adNode,adFields,adEdge = 'accounts','birthday,first_name' ,2,'insights?metric=post_activity,page_engaged_users,page_impressions','link,category',"campaign","name","insights"

    indexOfAccount = 0 ; # from the users accounts (pages to manage) changed by Abdelhak from 2 to 0 (got an error)

    if request.user.is_authenticated:
        cef = request.user
        for o in SocialAccount.objects.all():
            print("aaa")
            print(o)
        # response = requests.get('https://graph.facebook.com/me/feed')
        # data = response.json()
        token = SocialToken.objects.filter(account__user=request.user, account__provider='facebook')
        graph = facebook.GraphAPI(access_token=token, version="3.0")#"2.7")
        # posts = graph.get_connections(id='me', connection_name='posts')
        # likes = graph.get_connections(id='me', connection_name='likes')
        accounts = graph.get_connections(id='me', connection_name='accounts')
        pages = [page for page in accounts['data'] ]
        idsAndTokens = []
        pageNames = []

        for page in pages:
            idsAndTokens.append([page['id'],page['access_token'],page['name']])
            pageNames.append((page['id'],page['name']))

        pageToQuery = idsAndTokens[indexOfAccount]

        # graphPage = facebook.GraphAPI(access_token=idsAndTokens[0][1])
        if request.method == 'POST':
            form = MyTestForm(request.POST , choices=pageNames)
            if form.is_valid():
                sujet = form.cleaned_data.get('sujet')
                profilConnection = form.cleaned_data.get('profilConnection')
            #    print(request.POST)
                profilFields = form.cleaned_data.get('profilFields')
                pageConnection = form.cleaned_data.get('pageConnection')

                pageId = form.cleaned_data.get('pageAccount')
                pageToQuery = list(filter(lambda a: a[0] == pageId, idsAndTokens))[0]
                print("Page Account:")
                print(pageAccount)
                pageFields = form.cleaned_data.get('pageFields')
        else:
            form = MyTestForm(initial={'sujet': 'foo', 'profilConnection': profilConnection,'profilFields': profilFields,'pageAccount': pageNames,'pageConnection': pageConnection,'pageFields': pageFields, 'adNode':adNode,'adFields':adFields,'adEdge':adEdge}, choices=pageNames)


        #now we make the requests, in case of posts the user chose, else it's the default values

        graphPage = facebook.GraphAPI(access_token=pageToQuery[1],version="3.0")
        #pageInfo = graphPage.get_object(id=idsAndTokens[0][0], fields='link,category,is_published')

        ###" here THE DYNAMIC SHIT"
        profilConnection = graph.get_connections(id='me', connection_name=profilConnection)
        profilFields = graph.get_object(id='me', fields=profilFields)
        pageConnection = graphPage.get_connections(id=pageToQuery[0], connection_name=pageConnection) # id of second page it was [0][0]
        pageInfo = graphPage.get_object(id=pageToQuery[0], fields=pageFields)
        #this is to be seen after clarifying things with samir
        #print("post info ",graphPage.get_connections(id='420171028123844_1185907028216903', connection_name='insights?metric=post_engaged_users'))
        # field for number of likes in fan_count pageInfo = graphPage.get_object(id=pageToQuery[0], fields='fan_count')
        profilFields = json.JSONEncoder().encode(profilFields)
        pageFields = json.JSONEncoder().encode(pageFields)
        pageConnection = json.dumps(pageConnection, indent = 4)
        #print(pageConnection)

        ### Facebook Ads


#Initialize a new Session and instantiate an API object:
    # if request.user.is_authenticated:
    #     my_app_id = '217964325484293'
    #     my_app_secret = '9594c58c2d895491856ccfda5852955a'
    #     my_access_token = str(token[0])
    #     FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
    #     adAccounts = graph.get_connections(id='me', connection_name='adaccounts')
    #
    #     account = AdAccount(adAccounts['data'][1]['id'])
    #     users = account.get_users()
    #     print("Ads : \n\n\n")
    #     print(adAccounts)
    #     print(users)
    #     compaignNames = []
    #     for i in range(6):
    #         c = account.get_campaigns()[i]
    #         campaign = c.remote_read(fields=[Campaign.Field.name])
    #         compaignNames.append(campaign[Campaign.Field.name])
    #     someCampaignInsights = account.get_campaigns()[0].get_insights()


        # print(account.get_ads())
        # # print(my_account)
        # print(campaigns)


    return render(request, 'profile.html', locals())


def profileGoogleAnalytics(request):
    DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
    VIEW_ID = '103592216'
    token = SocialToken.objects.filter(account__user=request.user, account__provider='google')
    token = token[0].token
    print(token)
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
          'dateRanges': [{'startDate': '2018-09-25', 'endDate': '2018-10-01'}],
          'dimensions': [{'name': 'ga:acquisitionTrafficChannel'}],
          'metrics': [{'expression': 'ga:sessions'}]
        }]
      }
    ).execute()
    #printing data
    response_data = response.get('reports',[])[0]

    # metric_value = int(response_data.get('data', {}).get('rows', [])[0].get('metrics', [])[0].get('values', [])[0])
    # metric_dic = {
    #     'ga:users': metric_value
    # }
    # JSONFormatedAPIDATA = json.dumps(metric_dic, indent=3)


    parsed_data = parse_line_data(response_data)

    print(parsed_data) #dataFrame

    return render(request, 'profileGoogle.html', locals())


def profileGoogle(request):
    token = SocialToken.objects.filter(account__user=request.user, account__provider='google')
    token = token[0].token
    # credentials = AccessTokenCredentials(token,'Google API for Python')
    # http = httplib2.Http()
    # http = credentials.authorize(http)


    client_customer_id = "227-188-3391" # LG Electronics Algeria
    user_agent = 'Google API for Python'
    developer_token = 'C9npOKuEjmma0aTphIKdmg'
    token_expiry = datetime.datetime(2019, 1, 1, 12)
    oauth2_client = oauth2.GoogleAccessTokenClient(token, token_expiry)

    adwords_client = adwords.AdWordsClient(
        developer_token, oauth2_client, user_agent,
        client_customer_id=client_customer_id)

    customer = adwords_client.GetService('CustomerService').getCustomers()[0]
    print('You are logged in as customer: %s' % customer['customerId'])
    get_performance_metric(adwords_client)
    #    credentials = google.oauth2.credentials.Credentials(token)
    #authed_http = AuthorizedHttp(credentials)
    # http = httplib2.Http()
    # http = credentials.authorize(http)
    return render(request, 'profileGoogle.html', locals())

def get_performance_metric(adwords_client):
    # Initialize appropriate service.
    report_downloader = adwords_client.GetReportDownloader(version='v201809')

    # Create report query.
    report_query = (adwords.ReportQueryBuilder()
                    .Select( 'Clicks, Date')
                    .From('ACCOUNT_PERFORMANCE_REPORT')
                    .During('LAST_7_DAYS')
                    .Build())
    result = report_downloader.DownloadReportAsStringWithAwql(
        report_query, 'CSV', skip_report_header=True, skip_column_header=True,
        skip_report_summary=True, include_zero_impressions=False)


    print("the result from adwords api is : \n",result)


def get_compaigns(client):
    PAGE_SIZE = 100

    # Initialize appropriate service.
    campaign_service = client.GetService('CampaignService', version='v201809')

    # Construct selector and get all campaigns.
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True
    while more_pages:
        page = campaign_service.get(selector)
        # Display results.
        if 'entries' in page:
            for campaign in page['entries']:
                print(('Campaign with id "%s", name "%s", and status "%s" was '
                       'found.' % (campaign['id'], campaign['name'],
                                   campaign['status'])))
        else:
            print('No campaigns were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


def index(request):
    props = {}
    return render(request,'reporting_index.html', locals())


#Parse the response of API
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

        #In case of a second date range, do the same thing for the second request
        if len(metrics) == 2:
            row_temp2 = []
            for d in dimensions:
                row_temp2.append(d)
            for m in metrics[1]['values']:
                row_temp2.append(m)

    #Putting those list formats into pandas dataframe, and append them into the final result
    print(metrics_data)
    print(dimensions_data)
    result_object = {
        'metrics': metrics_data,
        'dimensions': dimensions_data
    }
    return result_object

def parse_response(report):

    """Parses and prints the Analytics Reporting API V4 response"""
    #Initialize results, in list format because two dataframes might return
    result_list = []

    #Initialize empty data container for the two dateranges (if there are two that is)
    data_csv = []
    data_csv2 = []

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
            row_temp.append(d)
        for m in metrics[0]['values']:
            row_temp.append(m)
            data_csv.append(row_temp)

        #In case of a second date range, do the same thing for the second request
        if len(metrics) == 2:
            row_temp2 = []
            for d in dimensions:
                row_temp2.append(d)
            for m in metrics[1]['values']:
                row_temp2.append(m)
            data_csv2.append(row_temp2)

    #Putting those list formats into pandas dataframe, and append them into the final result
    print(data_csv)
    print(header_row)
    result_df = pandas.DataFrame(data_csv, columns=header_row)
    result_list.append(result_df)
    if data_csv2 != []:
        result_list.append(pandas.DataFrame(data_csv2, columns=header_row))

    return result_list

# @api_view(['GET', 'POST'])
# def getData(request):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
