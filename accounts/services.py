import string, random
import json
from tzlocal import get_localzone
from django.core.signing import Signer, BadSignature
from django.shortcuts import get_object_or_404
from accounts.enums import AccountStatus, CodeStatus
from accounts.models import Registration, Code, CashoutMethod, AddressInfo
from orders.models import Order, Customer
from core.enums import Settings
from core.models import CashoutMethods
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
        "contact_info": {"contact_number": registration.order.customer.contact_number},
        "address_info": [
            {
                "label": "Default",
                "address1": registration.order.address.address1,
                "address2": registration.order.address.address2,
                "city": registration.order.address.city,
                "zip": registration.order.address.zip,
                "province": registration.order.address.province,
                "country": registration.order.address.country,
                "is_default": True,
            }
        ],
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


def update_code_status(request):
    code = get_object_or_404(Code, code=request.data["code"])
    is_updated = code.activate_deactivate()
    return is_updated

def update_registration_status(registration):
    registration.registration_status = AccountStatus.CLOSED
    registration.save()


def activate_account_login(account, user):
    user["display_name"] = " ".join((account.first_name, account.last_name))
    user["user_type_name"] = "Member"
    account.user = create_new_user(user)
    account.account_status = AccountStatus.ACTIVE
    account.save()


def verify_code_details(request):
    code = get_object_or_404(Code, code=request.data["discount_code"])

    match code.status:
        case CodeStatus.ACTIVE:
            return True, "Code valid", code
        case CodeStatus.DEACTIVATED:
            return False, "Code invalid", {}


def attach_orders_to_registered_account(account, registration):
    orders = Order.objects.filter(customer=registration.order.customer).update(account=account)
    return orders


def create_new_cashout_method(request, account):
    cashout_method = request.data.get("cashout_method")
    cashout_method_obj = CashoutMethods.objects.get(id=cashout_method.get("method"))

    data = {
        "account": account,
        "account_name": cashout_method.get("account_name"),
        "account_number": cashout_method.get("account_number"),
        "method": cashout_method_obj,
        "other": cashout_method.get("others"),
    }

    created_cashout_method = CashoutMethod.objects.create(**data)

    return created_cashout_method


def transform_account_form_data_to_json(request):
    data = {}
    for key, value in request.items():
        if type(value) != str:
            data[key] = value
            continue
        if "{" in value or "[" in value:
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value
        else:
            data[key] = value

    if request.get("avatar_info['id']") is not None:
        data["avatar_info"] = {
            "id": request["avatar_info['id']"],
            "avatar": request["avatar_info['avatar']"],
        }

    return data


def undefault_all_address_info(request):
    return AddressInfo.objects.filter(account__user=request.user).update(is_default=False)
