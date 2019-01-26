from django.urls import path

from . import views

app_name = 'info'
urlpatterns = [
        path('',views.home,name='home'),
        path('item/',views.item_home,name='item_home'),
        path('university/',views.university_home,name='university_home'),
        path('university/<int:university_id>/',views.university,name='university'),
        path('university/add/',views.add_university,name='add_university'),
        path('university/edit/',views.edit_university,name='edit_university'),
        path('university/<int:university_id>/group/<int:group_id>',views.group,name='group'),
        path('university/<int:university_id>/addgroup/',views.add_group,name='add_group'),
        path('university/<int:university_id>/addadmission/',views.add_admission,name='add_admission')
        ]
