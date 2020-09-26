from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_postgres_extensions.models.fields import ArrayField
import os,time


class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Cover_Photo(models.Model):
    id = models.CharField(max_length=100,primary_key=True)
    page_name = models.CharField(max_length=30,default='GEN 42')
    offset_x = models.IntegerField(default=100)
    offset_y = models.IntegerField(default=100)
    source = models.TextField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.page_name

class Insights_Value(models.Model):
    insights_value_id = models.CharField(max_length=100,blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    end_time = models.CharField(max_length=70,blank=True, null=True)
    insight_name = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("insight_name", "end_time","insights_value_id"),)
    
    def __str__(self):
        return str(self.value) if self.value else ''

class Page_Insight(models.Model):
    page_insights_id = models.CharField(max_length=70,primary_key=True)
    title = models.CharField(max_length=100,blank=True, null=True)
    name = models.CharField(max_length=100,blank=True, null=True)
    period = models.CharField(max_length=100,blank=True, null=True)
    values = models.ManyToManyField(Insights_Value)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.page_insights_id) if self.page_insights_id else ''

class Account_Page(models.Model):
    name = models.CharField(max_length=100)
    page_id = models.CharField(max_length=100,primary_key=True)
    access_token = models.TextField(default="EAAt6AfVaOUABAE9aAp2RC33ojOV1Yygn0mFY4qXUL1xgJobZAFgq9O4YCqJQ3tC5Muf7v4eMxuuvv4xP4lJHT0gEyaRuMEwWF8pZAwWBp3dtdVAviTAJVIfQHZA4oyqO6t8k0KFzoDnaGWhGky1g8JiIIK1koYiesyBNzpbfeLp9qQEsHYTTNZAU04acTBECwWAyYtoaxKZBuhk8yUHZAx")
    category = models.CharField(max_length=100,blank=True, null=True)
    cover = models.ForeignKey(Cover_Photo,on_delete = models.CASCADE,blank=True, null=True)
    phone = models.CharField(max_length=100,blank=True, null=True)
    insights = models.ManyToManyField(Page_Insight)
    unseen_message_count = models.IntegerField(default=0,blank=True, null=True)
    unread_message_count = models.IntegerField(default=0,blank=True, null=True)
    unread_notif_count = models.IntegerField(default=0,blank=True, null=True)
    rating_count = models.IntegerField(default=0,blank=True, null=True)
    talking_about_count = models.IntegerField(default=0,blank=True, null=True)
    new_like_count = models.IntegerField(default=0,blank=True, null=True)
    fan_count = models.IntegerField(default=0,blank=True, null=True)
    is_owned = models.BooleanField(default=False,blank=True, null=True)
    name_with_location_descriptor = models.CharField(max_length=100,blank=True, null=True)
    offer_eligible = models.BooleanField(default=True,blank=True, null=True)
    overall_star_rating = models.IntegerField(default=0,blank=True, null=True)
    website = models.CharField(max_length=100,blank=True, null=True)
    supports_instant_articles = models.BooleanField(default=False,blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    verification_status = models.CharField(max_length=30,blank=True, null=True)
    posts = models.ManyToManyField("Post")
    last_update = models.CharField(max_length=30,blank=True, null=True)

    def __str__(self):
        return str(self.name) if self.name else ''


class Action(models.Model):
    action_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        unique_together = (("action_id", "action_type"),)

    def __str__(self):
        return self.action_type


class Cost_Per_Action_Type(models.Model):
    cost_per_action_type_id = models.CharField(max_length=100,primary_key=True)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.action_type

class Cost_Per_Outbound_Click(models.Model):
    cost_per_outbound_click_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = (("cost_per_outbound_click_id", "action_type"),)
    def __str__(self):
        return self.action_type

class Cost_Per_Thruplay(models.Model):
    cost_per_thruplay_id = models.CharField(max_length=100,primary_key=True)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.action_type

class Cost_Per_Unique_Action_Type(models.Model):
    cost_per_unique_action_type_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        unique_together = (("cost_per_unique_action_type_id", "action_type"),)

    def __str__(self):
        return self.action_type

class Cost_Per_Unique_Outbound_Click(models.Model):
    cost_per_unique_outbound_click_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        unique_together = (("cost_per_unique_outbound_click_id", "action_type"),)

    def __str__(self):
        return self.action_type

class Outbound_Clicks_Ctr(models.Model):
    outbound_clicks_ctr_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    value = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        unique_together = (("outbound_clicks_ctr_id", "action_type"),)

    def __str__(self):
        return self.action_type

class Attribution_Spec(models.Model):
    attribution_spec_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    window_days = models.CharField(max_length=100,blank=True, null=True)

    class Meta:
        unique_together = (("attribution_spec_id", "event_type"),)

    def __str__(self):
        return self.event_type

class Ad_Account_Insight(models.Model):
    actions = models.ManyToManyField(Action)
    clicks = models.CharField(max_length=100,blank=True, null=True)
    account_name = models.CharField(max_length=100,primary_key=True)
    date_start = models.CharField(max_length=100)
    date_stop = models.CharField(max_length=100,blank=True, null=True)
    cost_per_action_type = models.ManyToManyField(Cost_Per_Action_Type)
    cost_per_inline_link_click = models.CharField(max_length=100,blank=True, null=True)
    cost_per_inline_post_engagement = models.CharField(max_length=100,blank=True, null=True)
    cost_per_unique_click = models.CharField(max_length=100,blank=True, null=True)
    cost_per_unique_inline_link_click = models.CharField(max_length=100,blank=True, null=True)
    cost_per_unique_outbound_click = models.ManyToManyField(Cost_Per_Unique_Outbound_Click)
    cost_per_unique_action_type = models.ManyToManyField(Cost_Per_Unique_Action_Type)
    cost_per_outbound_click = models.ManyToManyField(Cost_Per_Outbound_Click)
    outbound_clicks_ctr = models.ManyToManyField(Outbound_Clicks_Ctr)
    cost_per_thruplay = models.ManyToManyField(Cost_Per_Thruplay)
    objective = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.account_name




class Ad_Targeting(models.Model):
    age_max = models.IntegerField(default=65)
    age_min = models.IntegerField(default=18)
    genders = models.TextField(blank=True, null=True)
    location_countries = models.TextField(blank=True, null=True)
    location_types = models.TextField(blank=True, null=True)
    publisher_platforms = models.TextField(blank=True, null=True)
    facebook_positions = models.TextField(blank=True, null=True)
    instagram_positions = models.TextField(blank=True, null=True)
    device_platforms = models.TextField(blank=True, null=True)




class Ad_Insight(models.Model):
    ad_id = models.CharField(max_length=100,blank=True, null=True)
    clicks = models.CharField(max_length=100,blank=True, null=True)
    conversion_rate_ranking = models.CharField(max_length=100,blank=True, null=True)
    cost_per_action_type = models.ManyToManyField(Cost_Per_Action_Type)
    cost_per_thruplay = models.ManyToManyField(Cost_Per_Thruplay)
    cpc = models.CharField(max_length=100,blank=True, null=True)
    cpm = models.CharField(max_length=100,blank=True, null=True)
    cpp = models.CharField(max_length=100,blank=True, null=True)
    ctr = models.CharField(max_length=100,blank=True, null=True) 
    date_start = models.CharField(max_length=100,blank=True, null=True)
    date_stop = models.CharField(max_length=100,blank=True, null=True)
    engagement_rate_ranking = models.CharField(max_length=100,blank=True, null=True)
    frequency = models.CharField(max_length=100,blank=True, null=True)
    impressions = models.CharField(max_length=100,blank=True, null=True)
    reach = models.CharField(max_length=100,blank=True, null=True)
    spend = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.ad_id



class Ad(models.Model):
    ad_id = models.CharField(max_length=100,primary_key=True)
    adset_id = models.CharField(max_length=100,blank=True, null=True)
    account_id = models.CharField(max_length=100,blank=True, null=True)
    name = models.CharField(max_length=300,blank=True, null=True)
    campaign_id = models.CharField(max_length=100,blank=True, null=True)
    targeting = models.ForeignKey(Ad_Targeting,on_delete=models.CASCADE,null=True)
    created_time = models.CharField(max_length=100,blank=True, null=True)
    updated_time = models.CharField(max_length=100,blank=True, null=True)
    status = models.CharField(max_length=100,blank=True, null=True) 
    insights = models.ManyToManyField(Ad_Insight)

    def __str__(self):
        return self.name



class Campaign(models.Model):
    campaign_id = models.CharField(max_length=100,primary_key=True)
    account_id = models.CharField(max_length=100,blank=True, null=True)
    name = models.CharField(max_length=300)
    objective = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    updated_time = models.CharField(max_length=100)
    stop_time = models.CharField(max_length=100)
    lifetime_budget = models.IntegerField(default=0)
    ads = models.ManyToManyField(Ad,related_name = 'Ad')

    def __str__(self):
        return self.name

class Ad_Account(models.Model):
    adaccount_id = models.CharField(max_length=100,primary_key=True)
    id =  models.CharField(max_length=40,blank=True, null=True)
    name = models.CharField(max_length=40,blank=True, null=True)
    account_status = models.CharField(max_length=30,blank=True, null=True)
    created_time = models.CharField(max_length=30,blank=True, null=True)
    owner_id = models.CharField(max_length=30,blank=True, null=True)
    age = models.CharField(max_length=20,blank=True, null=True)
    insights = models.ForeignKey(Ad_Account_Insight,on_delete=models.CASCADE,blank=True, null=True)
    campaigns = models.ManyToManyField(Campaign,related_name = 'Campaign')
    amount_spent = models.CharField(max_length=30,blank=True, null=True)
    attribution_spec = models.ManyToManyField(Attribution_Spec)
    balance = models.CharField(max_length=30,blank=True, null=True)
    can_create_brand_lift_study =models.CharField(max_length=30,blank=True, null=True)
    capabilities = models.TextField(blank=True, null=True)
    last_update = models.CharField(max_length=30,blank=True, null=True)
    last_update_campaigns = models.CharField(max_length=30,blank=True, null=True)
    def __str__(self):
        return self.name



class Post_actions(models.Model):
    like = models.CharField(max_length= 30)
    comment = models.CharField(max_length= 30)
    share = models.CharField(max_length= 30)
    
    def __str__(self):
        return self.comment

class Post(models.Model):
    post_id = models.CharField(max_length=100,primary_key=True)
    message = models.TextField(blank=True, null=True)
    message_tags = models.TextField(blank=True, null=True)
    # actions = models.ForeignKey(Post_actions,on_delete = models.CASCADE)
    created_time = models.CharField(max_length=100)
    is_instagram_eligible = models.BooleanField(default=False)
    comments_mirroring_domain = models.CharField(max_length=200)
    is_hidden = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    link = models.TextField(blank=True, null=True)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return str(self.message) if self.message else ''



class Experience_Campaign(models.Model):
    id = models.CharField(max_length=100,primary_key=True)
    name = models.CharField(max_length=200,blank=True, null=True)
    objective = models.CharField(max_length=100,blank=True, null=True)
    niche = models.CharField(max_length=100,blank=True, null=True)
    age_max = models.CharField(max_length=30,blank=True, null=True)
    age_min = models.CharField(max_length=30,blank=True, null=True)
    genders = models.CharField(max_length=100,blank=True, null=True)
    created_time = models.CharField(max_length=100,blank=True, null=True)
    cpc = models.CharField(max_length=100,blank=True, null=True)
    cpm = models.CharField(max_length=100,blank=True, null=True)
    cpp = models.CharField(max_length=100,blank=True, null=True)
    clicks = models.CharField(max_length=100,blank=True, null=True)
    frequency = models.CharField(max_length=100,blank=True, null=True)
    ctr = models.CharField(max_length=100,blank=True, null=True)
    location_types = models.CharField(max_length=100,blank=True, null=True)
    country = models.CharField(max_length=50,blank=True, null=True)
    citie = models.CharField(max_length=50,blank=True, null=True)
    region = models.CharField(max_length=50,blank=True, null=True)
    device_platforms = models.CharField(max_length=50,blank=True, null=True)
    publisher_platforms = models.CharField(max_length=50,blank=True, null=True)
    positions = models.CharField(max_length=50,blank=True, null=True)
    efficiency = models.FloatField(blank=True, null=True,default=0)

    def __str__(self):
        return self.name


class API(models.Model):
    name = models.CharField(max_length=30,blank=True, null=True)
    provider = models.CharField(max_length=30,blank=True, null=True)
    
    def __str__(self):
        return self.name

class Metric(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    API = models.ForeignKey(API,on_delete=models.PROTECT) # will raise an error when trying to delete API
    queryName = models.CharField(max_length=100,blank=True, null=True)

    def __str__(self):
        return self.queryName



#apply the following in console to migrate and update :
#python manage.py makemigrations
#python manage.py migrate
#apply this in manage.py shell
# from facebook_auth.models import API, Metric
# a1 = API(name="FacebookGraph",provider="Facebook")
# a2 = API(name="FacebookAds",provider="Facebook")
# a1.save()
# a2.save()
# m1 = Metric(name="action sur la page",description = "Le nombre de clics sur les coordonnées de votre Page et le bouton call-to-action.", API= a1,queryName= 'page_total_actions')
# m1.save() 
# m2 = Metric(name="interaction sur la page",description = "Le nombre de fois où des personnes ont interagi avec vos publications à travers des réactions, des commentaires, des 
# partages et autres.", API= a1,queryName= 'page_engaged_users')
# m2.save()
# m3 = Metric(name="action négative",description = "Nombre de fois où les personnes ont réagi de manière négative (par ex. retiré un J’aime ou masqué une publication).", 
# API= a1,queryName= 'page_negative_feedback')
# m3.save()
# m4 = Metric(name="fans page en ligne par heur",description = "Le nombre de vos fans qui ont vu n’importe quelle publication sur Facebook un jour donné, répartis par heure
#  de jour (PST/PDT).", API= a1,queryName= 'page_fans_online')
# m4.save()
# m5 = Metric(name="fans page en ligne",description = "Le nombre de clics sur les coordonnées de votre Page et le bouton call-to-action.", API= a1,queryName= 'page_fans_online_per_day')
# m5.save()
# m6 = Metric(name="nouveu fans page",description = "Nombre de nouvelles personnes qui ont aimé votre Page selon qu’elles ont payé ou pas payé.", API= a1,
# queryName= 'page_fan_adds_by_paid_non_paid_unique')
# m6.save()
# m7 = Metric(name="impréssions page",description = "Le nombre de fois où un contenu de votre Page ou la concernant s’est affiché sur l’écran d’une personne.
#  Cela inclut les publications, les stories, les visites, les pubs, les informations sociales sur les personnes qui interagissent avec votre Page et plus encore."
# , API= a1,queryName= 'page_impressions')
# m7.save()
# m8 = Metric(name="impréssions payé page",description = "Nombre de fois où du contenu de votre Page ou la concernant s’est affiché sur l’écran d’une personne via une distribution payée,
#  comme une pub.", API= a1,queryName= 'page_impressions_paid')
# m8.save()
# m9 = Metric(name="impréssions gratuit page",description = "Le nombre de fois où du contenu de votre Page ou la concernant s’est affiché sur l’écran d’une personne via une distribution gratuite.
#  Cela inclut les publications, les stories, les visites, les informations sociales des personnes qui interagissent avec votre Page et plus encore.", API= a1,queryName= 'page_impressions_organic')
# m9.save()
# m10 = Metric(name="post page impression",description = "Nombre de fois où les publications de votre Page se sont affichées sur l’écran d’une personne. Par publication on entend aussi les statuts,
#  les photos, les liens, les vidéos et plus encore.", API= a1,queryName= 'page_posts_impressions')
# m10.save()
# m11 = Metric(name="post page impression payé",description = "Nombre de fois où les publications de votre Page se sont affichées sur l’écran d’une personne via une distribution payée,
#  comme une pub.", API= a1,queryName= 'page_posts_impressions_paid')
# m11.save()
# m12 = Metric(name="post page impression gratuit",description = "Nombre de fois où les publications de votre Page se sont affichées sur l’écran d’une personne via une distribution gratuite.",
#  API= a1,queryName= 'page_posts_impressions_organic')
# m12.save()
# m13 = Metric(name="total J’aime par jour",description = "Total par jour des réactions J’aime sur une Page.", API= a1,queryName= 'page_actions_post_reactions_like_total')
# m13.save()
# m14 = Metric(name="total J’adore par jour",description = "Total par jour des réactions J’adore sur une page.", API= a1,queryName= 'page_actions_post_reactions_love_total ')
# m14.save()
# m15 = Metric(name="total Wouah par jour",description = "Total des réactions Wouah sur une Page par jour.", API= a1,queryName= 'page_actions_post_reactions_wow_total')
# m15.save()
# m16 = Metric(name="total Haha par jour",description = "Total par jour des réactions « Haha » sur une page.", API= a1,queryName= 'page_actions_post_reactions_haha_total')
# m16.save()
# m17 = Metric(name="total désolées par jour",description = "Total par jour des réactions désolées sur une page.", API= a1,queryName= 'page_actions_post_reactions_sorry_total')
# m17.save()
# m18 = Metric(name="total colère par jour",description = "Total par jour des réactions de colère sur une page.", API= a1,queryName= 'page_actions_post_reactions_anger_total')
# m18.save()
# m19 = Metric(name="nombre j'aime page",description = "Nombre total de personnes qui ont aimé votre page.", API= a1,queryName= 'page_fans')
# m19.save()
# m20 = Metric(name="fans par langue",description = "Ensemble de données linguistiques des personnes qui aiment votre page en fonction de la langue par défaut sélectionnée à l’accès à Facebook.",
#  API= a1,queryName= 'page_fans_locale')
# m20.save()
# m21 = Metric(name="destribution des fans par wilaya",description = "Ensemble des données Facebook de localisation des personnes qui aiment votre Page, triées par ville.",
#  API= a1,queryName= 'page_fans_city')
# m21.save()
# m22 = Metric(name="nombre de fans par pays",description = "Le nombre de personnes, agrégées par pays, qui aiment votre Page.
# Seuls les 45 pays comprenant le plus de personnes qui aiment votre page sont inclus.", API= a1,queryName= 'page_fans_country')
# m22.save()
# m23 = Metric(name="nombre de fans par age",description = "Le nombre de personnes qui ont vu une de vos publications au moins une fois,
# regroupé par âge et genre. Les données démographiques agrégées sont basées sur un certain nombre de facteurs tels que les informations liées
# à l’âge et au genre que fournissent les utilisateurs sur leur profil Facebook. Cette valeur est une estimation.", API= a1,queryName= 'page_fans_gender_age')
# m23.save()
# m24 = Metric(name="nouveau fans",description = "Le nombre de nouvelles personnes qui ont aimé votre Page.", API= a1,queryName= 'page_fan_adds')
# m24.save()
# m25 = Metric(name="j'aime retiré",description = "Retrait des J’aime de votre Page.", API= a1,queryName= 'page_fan_removes')
# m25.save()
# m26 = Metric(name="total video vus 3s",description = "Le nombre de fois où les vidéos de votre Page ont été lues pendant au moins 3 secondes 
# (ou presque en totalité lorsqu’elles sont plus courtes). Pour une même lecture vidéo, nous excluons les temps de relecture.", API= a1,queryName= 'page_video_views')
# m26.save()
# m27 = Metric(name="page video vue payé 3s",description = "Le nombre de fois où les vidéos promues de votre Page ont été lues pendant au moins 3 secondes 
# (ou presque en totalité lorsqu’elles sont plus courtes). Pour chaque impression de vidéo, nous comptons les vues séparément et excluons les temps de relecture.",
# API= a1,queryName= 'page_video_views_paid')
# m27.save()
# m28 = Metric(name="page video vue gratuit 3s",description = "Le nombre de fois où les vidéos de votre Page ont été lues pendant au moins 3 secondes
# (ou presque en totalité si elles sont plus courtes), par couverture organique. Pour une même lecture vidéo, nous excluons les temps de relecture.",
# API= a1,queryName= 'page_video_views_organic')
# m28.save()
# m29 = Metric(name="page video auto vue 3s",description = "Nombre de fois où les vidéos de votre Page ont été lues de manière automatique pendant au moins 3 secondes
# (ou presque en totalité si elles font moins de 3 secondes). Pour une même lecture vidéo, nous excluons les temps de relecture.", API= a1,queryName= 'page_video_views_autoplayed')
# m29.save()
# m30 = Metric(name="page video manuel vue 3s",description = "The number of times your Page's videos played for at least 3 seconds, or for nearly their total
# length if they're shorter than 3 seconds, after people clicked play. During a single instance of a video playing, we'll exclude any time spent replaying the video.",
# API= a1,queryName= 'page_video_views_click_to_play')
# m30.save()
# m31 = Metric(name="total video complet vue 30s",description = "Le nombre de fois où les vidéos de votre Page ont été lues pendant au moins 30 secondes 
# (ou presque en totalité si elles sont plus courtes). Pour une même lecture vidéo, nous excluons les temps de relecture.", API= a1,queryName= 'page_video_complete_views_30s')
# m31.save()
# m32 = Metric(name="video complet vue 30s payé",description = "Nombre de fois où les vidéos promues de votre Page ont été lues pendant au moins 30 secondes 
# (ou presqu’en totalité si elles sont plus courtes). Pour chaque impression de vidéo, nous comptons les vues séparément et excluons les temps de relecture.", 
# API= a1,queryName= 'page_video_complete_views_30s_paid')
# m32.save()
# m33 = Metric(name="video complet vue 30s gratuit",description = "Le nombre de fois où les vidéos de votre Page ont été lues pendant au moins 30 secondes 
# (ou presque en totalité si elles sont plus courtes), par couverture organique. Pour une même lecture vidéo, nous excluons les temps de relecture.", 
# API= a1,queryName= 'page_video_complete_views_30s_organic')
# m33.save()
# m34 = Metric(name="page vue par personne non connecté",description = "Nombre de fois où le profil d’une Page a été vu par des personnes non connectées à Facebook.", 
# API= a1,queryName= 'page_views_logout')
# m34.save()
# m35 = Metric(name="page vue par personne connecté",description = "Nombre de fois où le profil d’une Page a été vu par des personnes connectées sur Facebook.", 
# API= a1,queryName= 'page_views_logged_in_total')
# m35.save()
# m36 = Metric(name="cpm",description = "", API= a2,queryName= 'cpm')
# m36.save()
# m37 = Metric(name="cpc",description = "", API= a2,queryName= 'cpc')
# m37.save()
# m38 = Metric(name="Impressions",description = "impression sur la publicité", API= a2,queryName= 'impressions')
# m38.save()
# m39 = Metric(name="total reaction par type",description = "Total par jour et par type des réactions sur une page.", API= a1,queryName= 'page_actions_post_reactions_total')
# m39.save()
# m40 = Metric(name="Reach",description = "", API= a2,queryName= 'reach')
# m40.save()

#to fetch all
#Metric.objects.all()
#to delte all
#Metric.objects.all().delete()
