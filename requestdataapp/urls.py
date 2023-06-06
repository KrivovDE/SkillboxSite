from django.urls import path
from .views import process_get_view

appname = "requestdataapp"

urlpatterns = [
    path('get/', process_get_view, name='get_view'),

]
