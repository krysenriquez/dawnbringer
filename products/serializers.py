from rest_framework.serializers import ModelSerializer
from products.models import ProductType, Product, Price, PointValue, Offer


class ProductTypesSerializer(ModelSerializer):
    class Meta:
        model = ProductType
        fields = [
            "type",
        ]


class OffersSerializer(ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"


class PointValuesSerializer(ModelSerializer):
    class Meta:
        model = PointValue
        fields = "__all__"


class PricesSerializer(ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"


class ProductsSerializer(ModelSerializer):
    offers = OffersSerializer(many=True, required=False)
    prices = PointValuesSerializer(many=True, required=False)
    point_values = PricesSerializer(many=True, required=False)

    def create(self, validated_data):
        offers = validated_data.pop("offers")
        prices = validated_data.pop("prices")
        point_values = validated_data.pop("point_values")
        product = Product.objects.create(**validated_data)

        for offer in offers:
            Offer.objects.create(**offer, product=product)

        for price in prices:
            PointValue.objects.create(**price, product=product)

        for point_value in point_values:
            Price.objects.create(**point_value, product=product)

        return product

    def update(self, instance, validated_data):
        offers = validated_data.get("offers")
        prices = validated_data.get("prices")
        point_values = validated_data.get("point_values")

        instance.product_type = validated_data.get("product_type", instance.product_type)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.is_deleted = validated_data.get("is_deleted", instance.is_deleted)
        instance.save()

        keep_offers = []
        if offers:
            for offer in offers:
                if "id" in offer.keys():
                    if Offer.objects.filter(id=offers["id"]).exists():
                        e = Offer.objects.get(id=offers["id"])
                        e.offered_from = validated_data.get("offered_from", e.offered_from)
                        e.offered_to = validated_data.get("offered_to", e.offered_to)
                        e.is_offered = validated_data.get("is_offered", e.is_offered)
                        e.save()
                        keep_offers.append(e.id)
                    else:
                        continue
                else:
                    e = Offer.objects.create(**offer, account=instance)
                    keep_offers.append(e.id)

            for offer in instance.offers.all():
                if offer.id not in keep_offers:
                    offer.delete()

        keep_prices = []
        if prices:
            for price in prices:
                if "id" in price.keys():
                    if Price.objects.filter(id=prices["id"]).exists():
                        e = Price.objects.get(id=prices["id"])
                        e.product_price = validated_data.get("product_price", e.product_price)
                        e.discount = validated_data.get("discount", e.discount)
                        e.save()
                        keep_prices.append(e.id)
                    else:
                        continue
                else:
                    e = Price.objects.create(**price, account=instance)
                    keep_prices.append(e.id)

            for price in instance.prices.all():
                if price.id not in keep_prices:
                    price.delete()

        keep_point_values = []
        if point_values:
            for point_value in point_values:
                if "id" in point_value.keys():
                    if PointValue.objects.filter(id=point_values["id"]).exists():
                        e = PointValue.objects.get(id=point_values["id"])
                        e.membership_level = validated_data.get("membership_level", e.membership_level)
                        e.point_value = validated_data.get("point_value", e.point_value)
                        e.save()
                        keep_point_values.append(e.id)
                    else:
                        continue
                else:
                    e = PointValue.objects.create(**point_value, account=instance)
                    keep_point_values.append(e.id)

            for point_value in instance.point_values.all():
                if point_value.id not in keep_point_values:
                    point_value.delete()

    class Meta:
        model = Product
        fields = "__all__"
