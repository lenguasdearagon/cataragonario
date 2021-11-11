"""
URLConf for test suite.

"""
from django.conf.urls import include
from django.urls import path


urlpatterns = [
    path('api/', include('cataragonario.urls')),
]
