from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from headcount.views import HeadcountViewSet
from turnover.views import TurnoverViewSet

router = routers.DefaultRouter()
router.register('headcount', HeadcountViewSet, basename='headcount')
router.register('turnover', TurnoverViewSet, basename='turnover')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls))
]
