from django.urls import path

from . import views_importer

urlpatterns = [
    path('validator/', views_importer.ImportMultiVariationValidatorView.as_view(), name='catalan-validator'),
    path('validator/logs/<name>/', views_importer.ImportLogView.as_view(), name='catalan-validator-log'),
]
