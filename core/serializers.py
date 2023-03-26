from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts.models import CashoutMethod
from core.models import Setting, MembershipLevel, Activity, ActivityDetails, CashoutMethods
from core.services import get_cashout_processing_fee_percentage
from orders.models import Order


class ContentTypeOrderInfoSerializer(ModelSerializer):
    order_number = serializers.CharField(source="get_order_number", required=False)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "order_number",
        ]


class ContentTypeCashoutMethodSerializer(ModelSerializer):
    cashout_method_name = serializers.CharField(source="get_cashout_method", required=False)
    method_name = serializers.CharField(source="get_cashout_method_name", required=False)

    class Meta:
        model = CashoutMethod
        fields = ["account_name", "account_number", "method", "method_name", "cashout_method_name"]
        read_only_fields = ("account",)


class ContentTypeActivitiesSerializer(ModelSerializer):
    activity_summary = serializers.CharField(source="get_activity_summary", required=False)
    activity_number = serializers.CharField(source="get_activity_number", required=False)
    account_name = serializers.CharField(source="account.get_full_name", required=False)
    account_number = serializers.CharField(source="account.get_account_number", required=False)
    membership_level_name = serializers.CharField(source="membership_level.name", required=False)

    class Meta:
        model = Activity
        fields = ["activity_number", "activity_type"]


class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, Order):
            serializer = ContentTypeOrderInfoSerializer(value)
        elif isinstance(value, CashoutMethod):
            serializer = ContentTypeCashoutMethodSerializer(value)
        elif isinstance(value, Activity):
            serializer = ContentTypeActivitiesSerializer(value)
        else:
            raise Exception("Unexpected type of content object")

        return serializer.data


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


class CreateUpdateCashoutMethodsSerializer(ModelSerializer):
    def update(self, instance, validated_data):
        instance.method_name = validated_data.get("method_name", instance.method_name)
        instance.is_disabled = validated_data.get("is_disabled", instance.is_disabled)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = CashoutMethods
        fields = "__all__"


class CashoutMethodsListSerializer(ModelSerializer):
    class Meta:
        model = CashoutMethods
        fields = [
            "id",
            "method_name",
        ]


class ActivityDetailsSerializer(ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = ActivityDetails
        fields = ["action", "created_by_username", "created", "created_by"]
        read_only_fields = ("activity",)


class CreateUpdateActivitySerializer(ModelSerializer):
    details = ActivityDetailsSerializer(many=True, required=False)

    def create(self, validated_data):
        details = validated_data.pop("details")
        activity = Activity.objects.create(**validated_data)

        for detail in details:
            ActivityDetails.objects.create(**detail, activity=activity)

        return activity

    def update(self, instance, validated_data):
        details = validated_data.get("details")

        instance.status = validated_data.get("status", instance.status)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.note = validated_data.get("note", instance.note)
        instance.save()

        if details:
            for detail in details:
                ActivityDetails.objects.create(**detail, activity=instance)

        return instance

    class Meta:
        model = Activity
        fields = "__all__"


class ActivitiesSerializer(ModelSerializer):
    details = ActivityDetailsSerializer(many=True, required=False)
    activity_summary = serializers.CharField(source="get_activity_summary", required=False)
    activity_number = serializers.CharField(source="get_activity_number", required=False)
    account_name = serializers.CharField(source="account.get_full_name", required=False)
    account_number = serializers.CharField(source="account.get_account_number", required=False)
    membership_level_name = serializers.CharField(source="membership_level.name", required=False)
    content_type_label = serializers.CharField(source="content_type.app_label", required=False)
    content_object = ContentObjectRelatedField(queryset=Activity.objects.all())

    class Meta:
        model = Activity
        fields = [
            "details",
            "activity_summary",
            "account_number",
            "activity_number",
            "account_name",
            "wallet",
            "membership_level_name",
            "activity_type",
            "activity_amount",
            "created",
            "modified",
            "status",
            "content_type_label",
            "content_object",
        ]


class ActivityCashoutListSerializer(ModelSerializer):
    activity_number = serializers.CharField(source="get_activity_number", required=False)
    account_name = serializers.CharField(source="account.get_full_name", required=False)
    account_number = serializers.CharField(source="account.get_account_number", required=False)

    def retrieve_activity_amount_total(self, activity_amount):
        total_tax = (100 - get_cashout_processing_fee_percentage()) / 100
        return "{:.2f}".format(activity_amount * total_tax)

    def retrieve_activity_amount_tax(self, activity_amount):
        total_tax = get_cashout_processing_fee_percentage() / 100
        return "{:.2f}".format(activity_amount * total_tax)

    def retrieve_company_tax(self):
        total_tax = get_cashout_processing_fee_percentage()
        return "{:.2f}".format(total_tax)

    def to_representation(self, instance):
        activity_amount_total = self.retrieve_activity_amount_total(instance.activity_amount)
        activity_amount_total_tax = self.retrieve_activity_amount_tax(instance.activity_amount)
        company_earning_tax = self.retrieve_company_tax()
        data = super(ActivityCashoutListSerializer, self).to_representation(instance)
        data.update(
            {
                "activity_amount_total": activity_amount_total,
                "company_earning_tax": company_earning_tax,
                "activity_amount_total_tax": activity_amount_total_tax,
            }
        )

        return data

    class Meta:
        model = Activity
        fields = [
            "activity_number",
            "activity_amount",
            "account_name",
            "account_number",
            "wallet",
            "status",
            "created",
        ]


class ActivityCashoutInfoSerializer(ModelSerializer):
    details = ActivityDetailsSerializer(many=True, required=False)
    activity_summary = serializers.CharField(source="get_activity_summary", required=False)
    account_name = serializers.CharField(source="account.get_full_name", required=False)
    account_number = serializers.CharField(source="account.get_account_number", required=False)
    activity_number = serializers.CharField(source="get_activity_number", required=False)
    content_object = ContentObjectRelatedField(queryset=Activity.objects.all())

    def retrieve_activity_amount_total(self, activity_amount):
        total_tax = (100 - get_cashout_processing_fee_percentage()) / 100
        return "{:.2f}".format(activity_amount * total_tax)

    def retrieve_activity_amount_tax(self, activity_amount):
        total_tax = get_cashout_processing_fee_percentage() / 100
        return "{:.2f}".format(activity_amount * total_tax)

    def retrieve_company_tax(self):
        total_tax = get_cashout_processing_fee_percentage()
        return "{:.2f}".format(total_tax)

    def to_representation(self, instance):
        activity_amount_total = self.retrieve_activity_amount_total(instance.activity_amount)
        activity_amount_total_tax = self.retrieve_activity_amount_tax(instance.activity_amount)
        company_earning_tax = self.retrieve_company_tax()
        data = super(ActivityCashoutInfoSerializer, self).to_representation(instance)
        data.update(
            {
                "activity_amount_total": activity_amount_total,
                "company_earning_tax": company_earning_tax,
                "activity_amount_total_tax": activity_amount_total_tax,
            }
        )

        return data

    class Meta:
        model = Activity
        fields = [
            "activity_number",
            "wallet",
            "account_name",
            "account_number",
            "activity_type",
            "activity_amount",
            "note",
            "activity_summary",
            "created",
            "modified",
            "status",
            "details",
            "content_object",
        ]
