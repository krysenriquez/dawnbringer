from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from settings.models import Branch, BranchAssignment, Company, DeliveryArea


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "description", "logo"]


class BranchesListSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", required=False)

    class Meta:
        model = Branch
        fields = [
            "branch_id",
            "branch_name",
            "is_main",
            "can_deliver",
            "can_supply",
            "is_active",
            "created_by_name",
        ]


class BranchInfoSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", required=False)

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
            "is_active",
            "created",
            "created_by_name",
        ]


class BranchAssignmentsSerializer(ModelSerializer):
    branch = BranchInfoSerializer(read_only=True, many=True)

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
