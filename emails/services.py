from django.core.mail import EmailMessage, get_connection
from django.core.mail.backends.smtp import EmailBackend
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.template.loader import render_to_string
from core.enums import Settings
from core.services import get_setting
from emails.models import EmailAddress, EmailTemplates
from settings.models import Company
from settings.serializers import CompanySerializer


def get_main_email_settings():
    return EmailAddress.objects.all().first()


def render_template(template, context):
    company = get_object_or_404(Company, id=1)
    serialized_company = CompanySerializer(company)
    context["company"] = serialized_company.data

    api_domain = str(get_setting(Settings.API_DOMAIN))
    context["base_url"] = api_domain

    return render_to_string(template, context)


def send_email(connection, from_email, subject, body, to_email):
    try:
        email_msg = EmailMessage(
            connection=connection,
            subject=subject,
            body=body,
            from_email=from_email,
            to=[to_email],
            reply_to=[from_email],
        )
        email_msg.content_subtype = "html"
        email_msg.send()
        return "Email Sent"
    except:
        return "Email failed, try again later."


def construct_and_send_email_payload(subject, body, to_email):
    email_settings = get_main_email_settings()

    connection = get_connection(
        host=email_settings.server_host,
        port=email_settings.server_port,
        username=email_settings.server_host_user,
        password=email_settings.server_host_password,
        use_tls=email_settings.server_use_tls,
        use_ssl=email_settings.server_use_ssl,
    )

    email_msg = send_email(
        connection=connection,
        from_email=email_settings.server_host_user,
        subject=subject,
        body=body,
        to_email=to_email,
    )
    return email_msg
