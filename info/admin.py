from django.contrib import admin

# Register your models here.
from .models import University,AdmissionData,DiscussGroup,Item

admin.site.register([University,AdmissionData,DiscussGroup,Item])
