from django.shortcuts import get_object_or_404
from products.models import ProductMedia, Branch


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


def create_variant_initial_transfer(request):
    main = get_object_or_404(Branch, branch_name="Main Office")

    transfer = [
        {
            "branch": main.pk,
            "quantity": request.data["quantity"],
            "comment": "Initial Quantity Record",
            "created_by": request.user.pk,
        }
    ]

    return transfer


def process_media(variant, media):
    has_failed_upload = False
    print(media)
    print(len(media))
    if len(media) > 0:
        attachments_dict = dict((media).lists())

        for attachment in attachments_dict:
            data = {"variant": variant, "attachment": attachment}
            success = ProductMedia.objects.create(**data)
            if success is None:
                has_failed_upload = True

        return has_failed_upload
