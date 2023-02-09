import json
from django.shortcuts import get_object_or_404
from products.models import ProductMedia, ProductType
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


def process_product_request(data):
    product_type = ProductType.objects.get(product_type_id=data["product_type"])

    data["product_type"] = product_type.pk
    print(data)
    return data


def process_variant_request(request):
    media = []

    data = {
        "product": request.data["product"],
        "sku": request.data["sku"],
        "variant_name": request.data["variant_name"],
        "variant_description": request.data["variant_description"],
        "variant_status": request.data["variant_status"],
        "price": request.data["price"],
        "meta": request.data["meta"],
        "point_values": request.data["point_values"],
        "created_by": request.user.pk,
    }

    if request.data["media"]:
        media = request.data["media"]

    data["supplies"] = create_variant_initial_transfer(request)

    return data, media


def create_variant_initial_transfer(data, request):
    main = get_object_or_404(Branch, branch_name="Main Office")

    transfer = [
        {
            "branch": main.pk,
            "quantity": data["quantity"],
            "comment": "Initial Quantity Record",
            "created_by": request.user.pk,
        }
    ]

    return transfer


def process_media(variant, request):
    has_failed_upload = False
    attachments_dict = dict((request).lists())["media"]

    for attachment in attachments_dict:
        data = {"variant": variant, "attachment": attachment}
        success = ProductMedia.objects.create(**data)
        if success is None:
            has_failed_upload = True

    return has_failed_upload
