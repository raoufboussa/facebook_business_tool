from django.contrib import admin
from .models import (Campaign,Account_Page,Ad_Account,API,Cover_Photo,
Attribution_Spec,Cost_Per_Action_Type,Cost_Per_Outbound_Click,Ad_Insight,
Cost_Per_Thruplay,Cost_Per_Unique_Action_Type,Cost_Per_Unique_Outbound_Click,
Ad_Account_Insight,Action,Metric,Insights_Value,Page_Insight,UserProfile,Ad,
Ad_Targeting,Post,Experience_Campaign)


admin.site.register(Campaign)
admin.site.register(API)
admin.site.register(Account_Page)
admin.site.register(Ad_Account)
admin.site.register(Cover_Photo)
admin.site.register(Attribution_Spec)
admin.site.register(Cost_Per_Action_Type)
admin.site.register(Cost_Per_Outbound_Click)
admin.site.register(Cost_Per_Unique_Action_Type)
admin.site.register(Cost_Per_Thruplay)
admin.site.register(Cost_Per_Unique_Outbound_Click)
admin.site.register(Ad_Account_Insight)
admin.site.register(Action)
admin.site.register(Metric)
admin.site.register(Page_Insight)
admin.site.register(Insights_Value)
admin.site.register(UserProfile)
admin.site.register(Ad)
admin.site.register(Ad_Targeting)
admin.site.register(Ad_Insight)
admin.site.register(Experience_Campaign)
admin.site.register(Post)

