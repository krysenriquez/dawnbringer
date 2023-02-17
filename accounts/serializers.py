from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts.models import Account, PersonalInfo, ContactInfo, AddressInfo, AvatarInfo, Code


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
        instance.file_name = validated_data.get("file_name", instance.file_name)
        instance.file_attachment = validated_data.get("file_attachment", instance.file_attachment)
        instance.save()

        return instance

    class Meta:
        model = AvatarInfo
        fields = [
            "id",
            "file_name",
            "file_attachment",
        ]
        read_only_fields = ("account",)


class CodeSerializer(ModelSerializer):
    class Meta:
        model = Code
        fields = ["code", "status"]
        read_only_fields = ("account",)


class AccountSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    personal_info = PersonalInfoSerializer(required=False)
    contact_info = ContactInfoSerializer(required=False)
    address_info = AddressInfoSerializer(required=False)
    avatar_info = AvatarInfoSerializer(required=False)
    code = CodeSerializer(required=False)
    referrer_name = serializers.CharField(source="self.referrer.get_fullname", required=False)

    def create(self, validated_data):
        personal_info = validated_data.pop("personal_info")
        contact_info = validated_data.pop("contact_info")
        address_info = validated_data.pop("address_info")
        avatar_info = validated_data.pop("avatar_info")
        code = validated_data.pop("code")
        account = Account.objects.create(**validated_data)

        PersonalInfo.objects.create(**personal_info, account=account)
        ContactInfo.objects.create(**contact_info, account=account)
        AddressInfo.objects.create(**address_info, account=account)
        AvatarInfo.objects.create(**avatar_info, account=account)
        Code.objects.create(**code, account=account)

        return account

    def update(self, instance, validated_data):
        personal_info = validated_data.get("personal_info")
        contact_info = validated_data.get("contact_info")
        address_info = validated_data.get("address_info")
        avatar_info = validated_data.get("avatar_info")
        code = validated_data.get("code")

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

        if address_info:
            if "id" in address_info.keys():
                if AddressInfo.objects.filter(id=address_info["id"]).exists():
                    e = AddressInfo.objects.get(id=address_info["id"])
                    e.address1 = validated_data.get("address1", address_info["address1"])
                    e.address2 = validated_data.get("address2", address_info["address2"])
                    e.city = validated_data.get("city", address_info["city"])
                    e.zip = validated_data.get("zip", address_info["zip"])
                    e.province = validated_data.get("province", address_info["province"])
                    e.country = validated_data.get("country", address_info["country"])
                    e.address_type = validated_data.get("address_type", address_info["address_type"])
                    e.save()
            else:
                e = AddressInfo.objects.create(**address_info, account=instance)

        if avatar_info:
            if "id" in avatar_info.keys():
                if AvatarInfo.objects.filter(id=avatar_info["id"]).exists():
                    e = AvatarInfo.objects.get(id=avatar_info["id"])
                    e.file_name = validated_data.get("file_name", avatar_info["file_name"])
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

        return instance

    class Meta:
        model = Account
        fields = "__all__"


class AccountListSerializer(ModelSerializer):
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
    personal_info = PersonalInfoSerializer(required=False)
    contact_info = ContactInfoSerializer(required=False)
    address_info = AddressInfoSerializer(required=False)
    avatar_info = AvatarInfoSerializer(required=False)
    referrer_name = serializers.CharField(source="referrer.get_fullname", required=False)
    referrer_account_number = serializers.CharField(source="referrer.get_account_number", required=False)
    full_name = serializers.CharField(source="get_full_name", required=False)
    account_number = serializers.CharField(source="get_account_number", required=False)
    user_status = serializers.CharField(source="user.is_active", required=False)

    class Meta:
        model = Account
        fields = "__all__"


class AccountAvatarSerializer(ModelSerializer):
    account_avatar = serializers.ImageField(source="avatar_info.file_attachment", required=False)
    account_name = serializers.CharField(source="get_full_name", required=False)
    account_number = serializers.CharField(source="get_account_number", required=False)
    account_code = serializers.CharField(source="code.code", required=False)

    class Meta:
        model = Account
        fields = ["account_id", "account_name", "account_number", "account_avatar", "account_code"]
