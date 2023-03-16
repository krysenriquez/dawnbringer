from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from core.models import Setting, MembershipLevel, Activity, ActivityDetails


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


class ActivityDetailsSerializer(ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = ActivityDetails
        fields = ["action", "created_by_username", "created", "created_by"]
        read_only_fields = ("activity",)


class ActivitiesSerializer(ModelSerializer):
    details = ActivityDetailsSerializer(many=True, required=False)
    activity_summary = serializers.CharField(source="get_activity_summary", required=False)
    activity_number = serializers.CharField(source="get_activity_number", required=False)
    account_name = serializers.CharField(source="account.get_full_name", required=False)
    account_number = serializers.CharField(source="account.get_account_number", required=False)

    class Meta:
        model = Activity
        fields = [
            "details",
            "activity_summary",
            "account_number",
            "activity_number",
            "account_name",
            "wallet",
            "activity_type",
            "activity_amount",
            "created",
            "modified",
            "status",
        ]
