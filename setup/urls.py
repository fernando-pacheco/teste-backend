from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from headcount.views import HeadcountViewSet

router = routers.DefaultRouter()
router.register('headcount', HeadcountViewSet, basename='headcount')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls))
]
