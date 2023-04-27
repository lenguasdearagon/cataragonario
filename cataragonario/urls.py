from django.urls import include, path
from linguatec_lexicon import views as aragonario_views
from rest_framework import routers

from . import views, views_importer

# Wire up our API using automatic URL routing.
router = routers.DefaultRouter()
router.register(r'gramcats', aragonario_views.GramaticalCategoryViewSet)
router.register(r'lexicons', aragonario_views.LexiconViewSet)
router.register(r'words', views.WordViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('validator/', views_importer.ImportMultiVariationValidatorView.as_view(), name='catalan-validator'),
    path('validator/logs/<name>/', views_importer.ImportLogView.as_view(), name='catalan-validator-log'),
]
