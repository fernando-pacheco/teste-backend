from django.shortcuts import render

from rest_framework import viewsets
from .serializer import HeadcountSerializer
from .models import Headcount

class HeadcountViewSet(viewsets.ModelViewSet):
    queryset = Headcount.objects.all()
    serializer_class = HeadcountSerializer
    http_method_names = ['get']