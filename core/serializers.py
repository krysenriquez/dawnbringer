from rest_framework.serializers import ModelSerializer
from core.models import Setting, MembershipLevel


class SettingsSerializer(ModelSerializer):
    def update(self, instance, validated_data):
        instance.value = validated_data.get("value", instance.value)
        instance.save()

        return instance

    class Meta:
        model = Setting
        fields = [
            "property",
            "value",
        ]


class MembershipLevelsSerializer(ModelSerializer):
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.level = validated_data.get("level", instance.level)
        instance.save()

        return instance

    class Meta:
        model = MembershipLevel
        fields = [
            "name",
            "level",
        ]
