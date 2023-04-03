import datetime
from django.core.signing import Signer, BadSignature
from tzlocal import get_localzone
from emails.services import construct_and_send_email_payload, render_template
from core.enums import Settings
from core.services import get_setting


def build_forgot_password_signed_object(user):
    signer = Signer()
    local_tz = get_localzone()
    expiration = datetime.datetime.now().astimezone(local_tz) + datetime.timedelta(minutes=5)
    data = {"user": user.pk, "email_address": user.email_address, "expiration": expiration.isoformat()}

    signed_obj = signer.sign_object(data)
    return signed_obj


def notify_customer_on_forgot_password_by_email(user, is_member):
    signed_obj = build_forgot_password_signed_object(user)

    if signed_obj:
        email_template = "emails/forgot-password.html"
        email_subject = "Forgot Password"

        if is_member:
            member_domain = str(get_setting(Settings.MEMBER_DOMAIN))
        else:
            member_domain = str(get_setting(Settings.ADMIN_DOMAIN))
        reset_password_link = str(get_setting(Settings.RESET_PASSWORD_LINK))

        email_body = render_template(
            email_template,
            {
                "display_name": user.display_name,
                "link": "".join((member_domain, reset_password_link, str(signed_obj))),
                "sub_title": "That's okay!",
                "title": email_subject + "?",
            },
        )
        return construct_and_send_email_payload(email_subject, email_body, user.email_address)


def verify_forgot_password_link(data):
    signer = Signer()
    try:
        unsigned_obj = signer.unsign_object(data)
        local_tz = get_localzone()
        is_expired = datetime.datetime.now().astimezone(local_tz) > datetime.datetime.fromisoformat(
            unsigned_obj["expiration"]
        )
        if not is_expired:
            return True, unsigned_obj

        return False, "Link Expired"
    except BadSignature:
        return False, "Invalid Link"
