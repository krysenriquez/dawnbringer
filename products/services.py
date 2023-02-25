import json
from django.shortcuts import get_object_or_404
from core.enums import Settings
from core.services import get_setting
from emails.services import construct_and_send_email_payload, get_email_template, render_template
from products.enums import SupplyStatus
from products.models import Product, ProductMedia, ProductVariant, Supply
from settings.models import Branch


def transform_form_data_to_json(request):
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
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value

    return data


def transform_variant_form_data_to_json(request):
    data = {}
    for key, value in request.items():
        if key == "media":
            continue
        if type(value) != str:
            data[key] = value
            continue
        if "{" in value or "[" in value:
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value
        else:
            try:
                data[key] = json.loads(value)
            except ValueError:
                data[key] = value

    return data


def create_variant_initial_supply(data, request):
    main = get_object_or_404(Branch, branch_name="Main Office")

    supply = [
        {
            "branch": main.pk,
            "quantity": data["quantity"],
            "comment": "Initial Quantity Record",
            "created_by": request.user.pk,
        }
    ]

    return supply


def process_media(variant, request):
    has_failed_upload = False
    keep_media = []
    if dict((request).lists()).get("media", None):
        attachments_dict = dict((request).lists())["media"]
        for attachment in attachments_dict:
            if type(attachment) != str:
                data = {"variant": variant, "attachment": attachment}
                e = ProductMedia.objects.create(**data)
                if e is not None:
                    keep_media.append(e.id)

                if e is None:
                    has_failed_upload = True
            else:
                e = ProductMedia.objects.get(id=attachment)
                keep_media.append(e.id)

    for attachment in variant.media.all():
        if attachment.id not in keep_media:
            attachment.delete()

    return has_failed_upload


def create_supply_status_filter(branch_id, supply_id, supply_status):
    StatusFilter = []
    supply = Supply.objects.get(supply_id=supply_id)

    # Both Supplier and Requestor
    if str(supply.branch_from.branch_id) == branch_id and str(supply.branch_to.branch_id) == branch_id:
        match supply_status:
            case SupplyStatus.PENDING:
                StatusFilter.append(SupplyStatus.CANCELLED)
                StatusFilter.append(SupplyStatus.REQUEST_RECEIVED)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.REQUEST_RECEIVED:
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.BACK_ORDERED:
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.PREPARING:
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
            case SupplyStatus.IN_TRANSIT:
                StatusFilter.append(SupplyStatus.DELIVERED)
            case _:
                pass
    # Requestor
    elif str(supply.branch_from.branch_id) == branch_id and str(supply.branch_to.branch_id) != branch_id:
        match supply_status:
            case SupplyStatus.PENDING:
                StatusFilter.append(SupplyStatus.REQUEST_RECEIVED)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.REQUEST_RECEIVED:
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.BACK_ORDERED:
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DENIED)
            case SupplyStatus.PREPARING:
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
            case _:
                pass
    # Requestor
    elif str(supply.branch_from.branch_id) != branch_id and str(supply.branch_to.branch_id) == branch_id:
        match supply_status:
            case SupplyStatus.PENDING:
                StatusFilter.append(SupplyStatus.CANCELLED)
            case SupplyStatus.IN_TRANSIT:
                StatusFilter.append(SupplyStatus.DELIVERED)
            case _:
                pass
    # Both
    else:
        pass
    print(StatusFilter)
    return StatusFilter


def process_supply_request(request):
    data = {
        "branch_from": request["branch_from"],
        "branch_to": request["branch_to"],
        "tracking_number": request["tracking_number"],
        "carrier": request["carrier"],
        "reference_number": request["reference_number"],
        "comment": request["comment"],
    }

    if request["details"]:
        details = []
        for detail in request["details"]:
            details.append({"variant": detail["variant"], "quantity": detail["quantity"]})
        data["details"] = details

    return data


def create_supply_initial_history(request):
    if request["set_status_to_delivered"]:
        return [{"supply_status": SupplyStatus.DELIVERED, "comment": "Same Branch Supply Request. Set to Delivered."}]

    return [{"supply_status": SupplyStatus.PENDING, "comment": "Supply Request Submitted"}]


def process_supply_history_request(request):
    supply = get_object_or_404(Supply, supply_id=request.data["supply_id"])

    if supply:
        data = {
            "supply": supply.pk,
            "supply_status": request.data["supply_status"],
            "comment": request.data["comment"],
            "email_sent": request.data["email_sent"],
            "created_by": request.user.pk,
        }

        return data


def notify_branch_to_on_supply_update_by_email(supply_history):
    supply = get_object_or_404(Supply, id=supply_history.supply.pk)
    branch_from = get_object_or_404(Branch, id=supply.branch_from.pk)
    branch_to = get_object_or_404(Branch, id=supply.branch_to.pk)

    if supply:
        template = "%s%s" % ("SUPPLY_", supply_history.supply_status)
        email_template = get_email_template(template)
        email_subject = render_template(email_template.subject, {})
        email_body = render_template(
            email_template.body,
            {
                "branch_from_name": branch_from.branch_name,
                "branch_to_name": branch_to.branch_name,
                "supply_number": supply.get_supply_number(),
            },
        )
        return construct_and_send_email_payload(email_subject, email_body, branch_to.email_address)

    return None


def verify_sku(request):
    sku = request.data["sku"]
    variant_id = request.data.get("variant_id", None)
    queryset = ProductVariant.objects.exclude(variant_id=variant_id).filter(sku=sku)
    if queryset.exists():
        return False
    return True


def verify_product_name(request):
    product_name = request.data["product_name"]
    product_id = request.data["product_id"]
    queryset = Product.objects.exclude(product_id=product_id).filter(product_name=product_name)
    if queryset.exists():
        return False
    return True
