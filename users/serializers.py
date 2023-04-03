from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from settings.models import BranchAssignment, Branch
from users.models import User, UserLogs, LogDetails, UserType, Module, Permission
from django.core.cache import cache
from django.conf import settings
import datetime


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    user = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = "__all__"

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    user = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = "__all__"

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ContentTypeSerializer(ModelSerializer):
    class Meta:
        model = ContentType
        fields = "__all__"


class UserBranchesListSerializer(ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)

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


class UserBranchAssignmentsSerializer(ModelSerializer):
    branch = UserBranchesListSerializer(read_only=True, many=True)

    class Meta:
        model = BranchAssignment
        fields = [
            "branch",
        ]


class UserLogsDetailsSerializer(ModelSerializer):
    class Meta:
        model = LogDetails
        fields = "__all__"
        read_only_fields = ("logDetails",)


class UserLogsSerializer(ModelSerializer):
    action_type_text = serializers.CharField(read_only=True)
    log_details = UserLogsDetailsSerializer(many=True, required=False)
    username = serializers.CharField(read_only=True)

    def create(self, validated_data):
        logDetails = validated_data.pop("logDetails")
        log = UserLogs.objects.create(**validated_data)

        for detail in logDetails:
            LogDetails.objects.create(**detail, logDetails=log)

        return log

    class Meta:
        model = UserLogs
        fields = "__all__"


class UsersListSerializer(ModelSerializer):
    user_type_name = serializers.CharField(source="user_type.user_type_name", required=False)
    created_by_name = serializers.CharField(source="created_by.display_name", required=False)
    # last_seen = serializers.CharField(source="get_last_seen", required=False)
    # online = serializers.BooleanField(source="get_online", required=False)
    online = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()

    def get_online(self, obj):
        if obj.last_seen:
            now = datetime.datetime.now()
            delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
            print(obj.last_seen)
            if now > obj.last_seen + delta:
                return False
            else:
                return True
        else:
            return False

    def get_last_seen(self, obj):
        last_seen = cache.get("seen_%s" % obj.username)
        obj.last_seen = last_seen
        return last_seen

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email_address",
            "display_name",
            "user_type_name",
            "is_active",
            "created_by_name",
            "last_seen",
            "online",
        ]


class UserInfoSerializer(ModelSerializer):
    user_type_name = serializers.CharField(source="user_type.user_type_name", required=False)
    branch_assignment = UserBranchAssignmentsSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "branch_assignment",
            "user_id",
            "avatar",
            "username",
            "email_address",
            "display_name",
            "user_type_name",
            "is_active",
        ]


class CreateUpdateUserSerializer(ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.display_name = validated_data.get("display_name", instance.display_name)
        instance.email_address = validated_data.get("email_address", instance.email_address)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.user_type = validated_data.get("user_type", instance.user_type)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.modified_by = self.context.get("request").user
        instance.save()

        return instance

    class Meta:
        model = User
        fields = "__all__"


class ModulesSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class PermissionsSerializer(ModelSerializer):
    module_name = serializers.CharField(source="module.module_name", required=False)

    class Meta:
        model = Permission
        fields = "__all__"

class UserPermissionsSerializer(ModelSerializer):
    module_name = serializers.CharField(source="module.module_name", required=False)

    class Meta:
        model = Permission
        fields = [
            "module_name",
            "can_create",
            "can_retrieve",
            "can_delete",
            "can_update",
        ]


class UserTypesOptionsSerializer(ModelSerializer):
    class Meta:
        model = UserType
        fields = ["id", "user_type_name"]


class UserTypesListSerializer(ModelSerializer):
    users_count = serializers.CharField(source="get_all_users_count", required=False)

    class Meta:
        model = UserType
        fields = ["id", "user_type_id", "users_count", "user_type_name"]


class UserTypeInfoSerializer(ModelSerializer):
    users_count = serializers.CharField(source="get_all_users_count", required=False)
    users = UsersListSerializer(many=True, required=False)
    permissions = PermissionsSerializer(many=True, required=False)

    class Meta:
        model = UserType
        fields = ["id", "user_type_id", "users_count", "user_type_name", "users", "permissions"]
