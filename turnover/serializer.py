from rest_framework import serializers
from .models import Turnover

class TurnoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turnover
        fields = '__all__'

class TurnoverLineChartSerializer(serializers.Serializer):
    init_date = serializers.DateField()
    end_date = serializers.DateField()

class TurnoverCategoryChartSerializer(serializers.Serializer):
    init_date = serializers.DateField()
    end_date = serializers.DateField()
    category = serializers.CharField()