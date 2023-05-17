from django.urls import path

from .views import schop_index, groups_list

appname = 'shopapp'

urlpatterns = [
    path('', schop_index, name='index'),
    path('groups/', groups_list, name='groups_list'),

]
