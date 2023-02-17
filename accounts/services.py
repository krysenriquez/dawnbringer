import string, random
import datetime
from tzlocal import get_localzone
from django.core.signing import Signer, BadSignature
from django.shortcuts import get_object_or_404
from accounts.enums import AccountStatus, CodeStatus
from accounts.models import Registration, Code
from orders.models import Order
from core.enums import Settings
from core.services import get_setting
from users.services import create_new_user


def generate_code():
    size = int(get_setting(Settings.CODE_LENGTH))
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(size))


def verify_registration_link(data):
    signer = Signer()
    try:
        unsigned_obj = signer.unsign_object(data)
        is_valid, registration = validate_registration(unsigned_obj)
        if is_valid:
            return True, "Valid Registration Link"
        return False, "Invalid Registration Link"
    except BadSignature:
        return False, "Invalid Registration Link"


def get_registration_link_object(data):
    signer = Signer()
    try:
        unsigned_obj = signer.unsign_object(data)
        is_valid, registration = validate_registration(unsigned_obj)
        return is_valid, registration
    except BadSignature:
        return False, {}


def validate_registration(data):
    registration = Registration.objects.get(id=data["registration_id"])
    if registration.registration_status == AccountStatus.PENDING:
        return True, registration
    return False, {}


def process_create_account_request(request, registration):
    data = {
        "first_name": request["first_name"],
        "middle_name": request["middle_name"],
        "last_name": request["last_name"],
        "personal_info": request["personal_info"],
        "contact_info": request["contact_info"],
        "address_info": request["address_info"],
        "avatar_info": request["avatar_info"],
    }

    order = Order.objects.get(id=registration.order.pk)
    if order.promo_code:
        data["referrer"] = order.promo_code.account.pk

    data["code"] = create_account_code()

    return data


def create_account_code():
    code = generate_code()
    account_code = {
        "code": code,
    }

    return account_code


def update_registration_status(registration):
    registration.registration_status = AccountStatus.CLOSED
    registration.save()


def activate_account_login(account, user):
    account.user = create_new_user(user)
    account.account_status = AccountStatus.ACTIVE
    account.save()


def verify_code_details(request):
    code = get_object_or_404(Code, code=request.data["activation_code"])

    match code.status:
        case CodeStatus.ACTIVE:
            return True, "Code valid", code
        case CodeStatus.DEACTIVATED:
            return False, "Code invalid", {}
