from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from emails.models import EmailInquiry


class EmailInquirySerializer(ModelSerializer):
    class Meta:
        model = EmailInquiry
        fields = ["subject", "email_address", "message"]
