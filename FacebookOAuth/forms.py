from django import forms

class MyTestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.myChoices = kwargs.pop('choices', None)
        super(MyTestForm, self).__init__(*args, **kwargs)
        #print(self.myChoices)
        self.fields['pageAccount'] = forms.ChoiceField(choices=self.myChoices )

    sujet = forms.CharField(max_length=100)
    profilConnection = forms.CharField(widget=forms.Textarea ,help_text=u"Ecrire ici une connection que vous voulez récupérer de votre PROFIL. Exemple : accounts ou posts oulikes ")
    profilFields = forms.CharField(widget=forms.Textarea ,help_text=u"Ecrire ici les fields que vous voulez récupérer de votre PAGE en les séparants avec virgule. Exemple : birthday, email,first_name ")
    pageAccount = forms.ChoiceField()
    pageConnection = forms.CharField(widget=forms.Textarea ,help_text=u"Ecrire ici une connection que vous voulez récupérer de votre page. Exemple : insights ou posts oulikes ")
    pageFields = forms.CharField(widget=forms.Textarea ,help_text=u"Ecrire ici les fields que vous voulez récupérer de votre PAGE en les séparants avec virgule. Exemple : link , category ")
    adNode = forms.CharField(max_length=100)
    adFields = forms.CharField(max_length=100)
    adEdge = forms.CharField(max_length=100)
from pseudoAPI.models import PeriodicReport,Report

class PeriodicCreateForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user')
        super(PeriodicCreateForm,self).__init__(*args,**kwargs)
        self.fields['report'].queryset = Report.objects.filter(user=user) # show only current user's reports
        self.fields['report'].label_from_instance = lambda obj: " %s" % ( obj.name)

    class Meta:
        model = PeriodicReport

        fields = ['name','report','periodInDays','nextRunDate','emailAddress']
        nextRunDate = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker'
                                }))
