from rest_framework import serializers
from .models import Region, CroppingStat, IrrigationArea

class RegionSerializer(serializers.ModelSerializer):
    # Expose land_holding, falling back to average_land_holding for backward data
    land_holding = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = '__all__'

    def get_land_holding(self, obj: Region):
        return obj.land_holding if obj.land_holding is not None else obj.average_land_holding


class CroppingStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CroppingStat
        fields = '__all__'


class IrrigationAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IrrigationArea
        fields = '__all__'
