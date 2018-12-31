from django.contrib import admin
from .models import Board,Update,File

# Register your models here.

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('date','title','get_summary',)

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('date','title',)

admin.site.register(File)
