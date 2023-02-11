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
