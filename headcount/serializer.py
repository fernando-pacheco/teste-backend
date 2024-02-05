from rest_framework import serializers
from .models import Headcount

class HeadcountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Headcount
        fields = '__all__'
