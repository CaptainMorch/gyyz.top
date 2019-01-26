from django.forms import ModelForm

from .models import University,DiscussGroup,AdmissionData

class UniversityForm(ModelForm):
    class Meta:
        model = University
        fields = '__all__'

class GroupForm(ModelForm):
    class Meta:
        model = DiscussGroup
        exclude = ['university','add_date']

class AdmissionData(ModelForm):
    class Meta:
        model = AdmissionData
        exclude = ['university']
