from rest_framework.serializers import ModelSerializer
from settings.models import Branch, BranchAssignment


class BranchesSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "branch_id",
            "branch_name",
            "is_main",
            "can_deliver",
            "can_supply",
        ]


class BranchAssignmentsSerializer(ModelSerializer):
    branch = BranchesSerializer(read_only=True, many=True)

    class Meta:
        model = BranchAssignment
        fields = [
            "branch",
        ]
