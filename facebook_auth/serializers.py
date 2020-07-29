from rest_framework import serializers
from livemap.models import Tag
from django.contrib.auth.models import User
from .models import (Campaign,Account_Page,Ad_Account,API,Cover_Photo,
Attribution_Spec,Cost_Per_Action_Type,Cost_Per_Outbound_Click,
Cost_Per_Thruplay,Cost_Per_Unique_Action_Type,Cost_Per_Unique_Outbound_Click,
Ad_Account_Insight,Action,Metric,Insights_Value,Page_Insight)


class Account_PageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Account_Page
        fields = '__all__'
