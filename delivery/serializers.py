from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from delivery.models import DeliveryArea, DeliveryBracket, DeliveryMethod, DeliveryMethodType


class DeliveryMethodTypeSerializer(ModelSerializer):
    class Meta:
        model = DeliveryMethodType
        fields = "__all__"


class DeliveryMethodSerializer(ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = "__all__"


class DeliveryBracketSerializer(ModelSerializer):
    class Meta:
        model = DeliveryBracket
        fields = "__all__"


class DeliveryAreaSerializer(ModelSerializer):
    class Meta:
        model = DeliveryArea
        fields = "__all__"
