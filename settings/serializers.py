from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from settings.models import Branch, BranchAssignment, Company, DeliveryArea
from users.models import User
from users.serializers import UsersListSerializer


class HistoricalRecordField(serializers.ListField):
    def to_representation(self, instance):
        histories = instance.all()
        old_record = None
        historical_data = []
        for history in histories.iterator():
            data = {}
            changes = []
            if old_record is None:
                old_record = history
            else:
                delta = old_record.diff_against(history)
                for change in delta.changes:
                    changes.append(
                        "{} changed from {} to {}".format(
                            change.field, change.old if change.old else "None", change.new if change.new else "None"
                        )
                    )
                old_record = history

            data["modified"] = history.modified
            if history.modified_by:
                data["modified_by"] = history.modified_by.username
            else:
                data["modified_by"] = None

            if len(changes) > 0:
                data["changes"] = changes
            else:
                data["changes"] = None

            historical_data.append(data)

        return super().to_representation(historical_data)


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "description", "logo", "domain", "email_address", "contact_number", "location"]


class BranchesListSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

    class Meta:
        model = Branch
        fields = [
            "id",
            "branch_id",
            "branch_name",
            "is_main",
            "can_deliver",
            "can_supply",
            "is_active",
            "created_by_name",
        ]


class BranchInfoSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)
    users = serializers.SerializerMethodField(source="get_users")
    history = HistoricalRecordField(read_only=True)

    def get_users(obj, branch):
        qs = User.objects.filter(branch_assignment__branch=branch)
        return UsersListSerializer(qs, many=True).data

    class Meta:
        model = Branch
        fields = [
            "users",
            "id",
            "branch_id",
            "branch_name",
            "address1",
            "address2",
            "city",
            "zip",
            "province",
            "country",
            "phone",
            "email_address",
            "is_main",
            "can_deliver",
            "can_supply",
            "is_active",
            "created",
            "created_by_name",
            "history",
        ]


class CreateBranchSerializer(ModelSerializer):
    def create(self, validated_data):
        branch = Branch.objects.create(**validated_data)

        return branch

    def update(self, instance, validated_data):
        instance.branch_name = validated_data.get("branch_name", instance.branch_name)
        instance.address1 = validated_data.get("address1", instance.address1)
        instance.address2 = validated_data.get("address2", instance.address2)
        instance.city = validated_data.get("city", instance.city)
        instance.zip = validated_data.get("zip", instance.zip)
        instance.province = validated_data.get("province", instance.province)
        instance.country = validated_data.get("country", instance.country)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.email_address = validated_data.get("email_address", instance.email_address)
        instance.is_main = validated_data.get("is_main", instance.is_main)
        instance.can_deliver = validated_data.get("can_deliver", instance.can_deliver)
        instance.can_supply = validated_data.get("can_supply", instance.can_supply)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = Branch
        fields = "__all__"


class BranchAssignmentsSerializer(ModelSerializer):
    branch = BranchesListSerializer(read_only=True, many=True)

    class Meta:
        model = BranchAssignment
        fields = [
            "branch",
        ]


class ShopBranchSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "branch_id",
            "branch_name",
            "address1",
            "address2",
            "city",
            "zip",
            "province",
            "country",
            "phone",
            "is_main",
            "can_deliver",
            "can_supply",
        ]


class ShopDeliveryAreaSerializer(ModelSerializer):
    class Meta:
        model = DeliveryArea
        fields = [
            "amount",
        ]
