import json
from django.shortcuts import get_object_or_404
from products.enums import SupplyStatus
from products.models import ProductMedia, Supply
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
    attachments_dict = dict((request).lists())["media"]

    for attachment in attachments_dict:
        data = {"variant": variant, "attachment": attachment}
        success = ProductMedia.objects.create(**data)
        if success is None:
            has_failed_upload = True

    return has_failed_upload


def create_supply_status_filter(branch_id, supply_id, supply_status):
    StatusFilter = []
    branch = Branch.objects.get(branch_id=branch_id)
    supply = Supply.objects.get(supply_id=supply_id)

    # Supplier
    if supply.branch_from == branch and supply.branch_to != branch:
        match supply_status:
            case SupplyStatus.PENDING:
                StatusFilter.append(SupplyStatus.ORDER_RECEIVED)
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DELIVERED)
            case SupplyStatus.ORDER_RECEIVED:
                StatusFilter.append(SupplyStatus.PENDING)
                StatusFilter.append(SupplyStatus.CANCELLED)
            case _:
                StatusFilter.append(SupplyStatus.CANCELLED)
    # Requestor
    elif supply.branch_from != branch and supply.branch_to == branch:
        match supply_status:
            case SupplyStatus.PENDING:
                StatusFilter.append(SupplyStatus.ORDER_RECEIVED)
                StatusFilter.append(SupplyStatus.BACK_ORDERED)
                StatusFilter.append(SupplyStatus.PREPARING)
                StatusFilter.append(SupplyStatus.IN_TRANSIT)
                StatusFilter.append(SupplyStatus.DELIVERED)
            case _:
                StatusFilter.append(SupplyStatus.CANCELLED)
    # Both
    else:
        pass

    return StatusFilter
