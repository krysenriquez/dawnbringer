from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts.models import Account, PersonalInfo, ContactInfo, AddressInfo, AvatarInfo, Code
from orders.serializers import OrdersListSerializer
from core.models import MembershipLevel
from core.serializers import ActivitiesSerializer
from core.enums import Settings
from core.services import get_setting


class PersonalInfoSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        instance.birthdate = validated_data.get("birthdate", instance.birthdate)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.save()

        return instance

    class Meta:
        model = PersonalInfo
        fields = ["id", "birthdate", "gender"]
        read_only_fields = ("account",)


class ContactInfoSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        instance.contact_number = validated_data.get("contact_number", instance.contact_number)
        instance.save()

        return instance

    class Meta:
        model = ContactInfo
        fields = ["id", "contact_number"]
        read_only_fields = ("account",)


class AddressInfoSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    full_address = serializers.CharField(source="get_full_address", required=False)

    def update(self, instance, validated_data):
        instance.address1 = validated_data.get("address1", instance.address1)
        instance.address2 = validated_data.get("address2", instance.address2)
        instance.city = validated_data.get("city", instance.city)
        instance.zip = validated_data.get("zip", instance.zip)
        instance.province = validated_data.get("province", instance.province)
        instance.country = validated_data.get("country", instance.country)
        instance.address_type = validated_data.get("address_type", instance.address_type)
        instance.save()

        return instance

    class Meta:
        model = AddressInfo
        fields = [
            "id",
            "address1",
            "address2",
            "city",
            "zip",
            "province",
            "country",
            "address_type",
            "full_address",
        ]
        read_only_fields = ("account",)


class AvatarInfoSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)

    def update(self, instance, validated_data):
        instance.file_attachment = validated_data.get("file_attachment", instance.file_attachment)
        instance.save()

        return instance

    class Meta:
        model = AvatarInfo
        fields = [
            "id",
            "file_attachment",
        ]
        read_only_fields = ("account",)


class CodeSerializer(ModelSerializer):
    def to_representation(self, instance):
        shop_code_link = get_setting(Settings.SHOP_CODE_LINK)
        string = [shop_code_link, instance.code]
        data = super(CodeSerializer, self).to_representation(instance)
        data.update({"referral_link": "".join(string)})

        return data

    class Meta:
        model = Code
        fields = ["code", "status"]
        read_only_fields = ("account",)


class CreateAccountSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    personal_info = PersonalInfoSerializer(required=False)
    contact_info = ContactInfoSerializer(required=False)
    address_info = AddressInfoSerializer(many=True, required=False)
    code = CodeSerializer(required=False)
    avatar_info = AvatarInfoSerializer(required=False)
    referrer_name = serializers.CharField(source="self.referrer.get_fullname", required=False)

    def create(self, validated_data):
        personal_info = validated_data.pop("personal_info")
        contact_info = validated_data.pop("contact_info")
        avatar_info = validated_data.pop("avatar_info")
        code = validated_data.pop("code")
        address_info = validated_data.pop("address_info")
        account = Account.objects.create(**validated_data)

        PersonalInfo.objects.create(**personal_info, account=account)
        ContactInfo.objects.create(**contact_info, account=account)
        AvatarInfo.objects.create(**avatar_info, account=account)
        Code.objects.create(**code, account=account)

        for address in address_info:
            AddressInfo.objects.create(**address, account=account)

        return account

    def update(self, instance, validated_data):
        personal_info = validated_data.get("personal_info")
        contact_info = validated_data.get("contact_info")
        avatar_info = validated_data.get("avatar_info")
        code = validated_data.get("code")
        address_info = validated_data.get("address_info")

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.middle_name = validated_data.get("middle_name", instance.middle_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.account_status = validated_data.get("account_status", instance.account_status)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.save()

        if personal_info:
            if "id" in personal_info.keys():
                if PersonalInfo.objects.filter(id=personal_info["id"]).exists():
                    e = PersonalInfo.objects.get(id=personal_info["id"])
                    e.birthdate = validated_data.get("birthdate", personal_info["birthdate"])
                    e.gender = validated_data.get("gender", personal_info["gender"])
                    e.save()
            else:
                e = PersonalInfo.objects.create(**personal_info, account=instance)

        if contact_info:
            if "id" in contact_info.keys():
                if ContactInfo.objects.filter(id=contact_info["id"]).exists():
                    e = ContactInfo.objects.get(id=contact_info["id"])
                    e.contact_number = validated_data.get("contact_number", contact_info["contact_number"])
                    e.save()
            else:
                e = ContactInfo.objects.create(**contact_info, account=instance)

        if avatar_info:
            if "id" in avatar_info.keys():
                if AvatarInfo.objects.filter(id=avatar_info["id"]).exists():
                    e = AvatarInfo.objects.get(id=avatar_info["id"])
                    e.file_attachment = validated_data.get("file_attachment", avatar_info["file_attachment"])
                    e.save()
            else:
                e = AvatarInfo.objects.create(**avatar_info, account=instance)

        if code:
            if "id" in code.keys():
                if Code.objects.filter(id=code["id"]).exists():
                    e = Code.objects.get(id=code["id"])
                    e.code = validated_data.get("code", code["code"])
                    e.status = validated_data.get("status", code["status"])
                    e.save()
            else:
                e = Code.objects.create(**code, account=instance)

        if address_info:
            keep_address_info = []
            for address in address_info:
                if "id" in address.keys():
                    if AddressInfo.objects.filter(id=address["id"]).exists():
                        e = AddressInfo.objects.get(id=address["id"])
                        e.is_default = validated_data.get("is_default", e.is_default)
                        e.label = validated_data.get("label", e.label)
                        e.address1 = validated_data.get("address1", e.address1)
                        e.address2 = validated_data.get("address2", e.address2)
                        e.city = validated_data.get("city", e.city)
                        e.zip = validated_data.get("zip", e.zip)
                        e.province = validated_data.get("province", e.province)
                        e.country = validated_data.get("country", e.country)
                        e.address_type = validated_data.get("address_type", e.address_type)
                        e.save()
                else:
                    e = AddressInfo.objects.create(**address, account=instance)
                    keep_address_info.append(e.id)

            for address in instance.address_info.all():
                if address.id not in address:
                    address.delete()

        return instance

    class Meta:
        model = Account
        fields = "__all__"


class AccountsListSerializer(ModelSerializer):
    account_name = serializers.CharField(source="get_account_name", required=False)
    account_number = serializers.CharField(source="get_account_number", required=False)
    referrer_account_name = serializers.CharField(source="referrer.get_account_name", required=False)
    referrer_account_number = serializers.CharField(source="referrer.get_account_number", required=False)
    user_status = serializers.CharField(source="user.is_active", required=False)

    class Meta:
        model = Account
        fields = [
            "account_id",
            "account_name",
            "account_number",
            "referrer_account_name",
            "referrer_account_number",
            "account_status",
            "user_status",
            "created",
        ]


class AccountInfoSerializer(ModelSerializer):
    code = CodeSerializer(required=False)
    personal_info = PersonalInfoSerializer(required=False)
    contact_info = ContactInfoSerializer(required=False)
    avatar_info = AvatarInfoSerializer(required=False)
    address_info = AddressInfoSerializer(many=True, required=False)
    orders = OrdersListSerializer(many=True, required=False)
    activities = ActivitiesSerializer(many=True, required=False)
    referrer_name = serializers.CharField(source="referrer.get_full_name", required=False)
    referrer_account_number = serializers.CharField(source="referrer.get_account_number", required=False)
    full_name = serializers.CharField(source="get_full_name", required=False)
    account_number = serializers.CharField(source="get_account_number", required=False)
    user_status = serializers.CharField(source="user.is_active", required=False)

    def to_representation(self, instance):
        data = super(AccountInfoSerializer, self).to_representation(instance)
        membership_levels = MembershipLevel.objects.all()
        if membership_levels:
            points = []
            for level in membership_levels:
                total = instance.get_membership_level_points(membership_level=level)
                points.append({"membership_level": level.name, "total_points": total})
            data.update({"membership_level_points": points})
        return data

    class Meta:
        model = Account
        fields = [
            "personal_info",
            "contact_info",
            "code",
            "avatar_info",
            "address_info",
            "orders",
            "activities",
            "referrer_name",
            "referrer_account_number",
            "full_name",
            "account_number",
            "account_status",
            "user_status",
        ]


class AccountAvatarSerializer(ModelSerializer):
    code = CodeSerializer(required=False)
    account_avatar = serializers.ImageField(source="avatar_info.file_attachment", required=False)
    account_name = serializers.CharField(source="get_full_name", required=False)
    account_number = serializers.CharField(source="get_account_number", required=False)

    def to_representation(self, instance):
        data = super(AccountAvatarSerializer, self).to_representation(instance)
        membership_levels = MembershipLevel.objects.all()
        if membership_levels:
            points = []
            for level in membership_levels:
                total = instance.get_membership_level_points(membership_level=level)
                points.append({"membership_level": level.name, "total_points": total})
            data.update({"membership_level_points": points})
        return data

    class Meta:
        model = Account
        fields = ["account_id", "account_name", "account_number", "account_avatar", "code"]
