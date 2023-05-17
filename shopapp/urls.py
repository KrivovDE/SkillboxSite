from django.urls import path

from .views import schop_index

appname = 'shopapp'
urlpatterns = [
    path('', schop_index, name='index'),
]
