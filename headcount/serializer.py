# serializers.py
from rest_framework import serializers
from .models import Headcount

class HeadcountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headcount
        fields = '__all__'

class HeadcountLineChartSerializer(serializers.Serializer):
    init_date = serializers.DateField()
    end_date = serializers.DateField()

class HeadcountCategoryChartSerializer(serializers.Serializer):
    init_date = serializers.DateField()
    end_date = serializers.DateField()
    category = serializers.CharField()
