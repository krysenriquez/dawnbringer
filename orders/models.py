import uuid
from django.db import models
from orders.enums import AddressType
from orders.enums import AddressType, OrderType, PaymentMethods, OrderStatus

# Orders
def order_attachments_directory(instance, filename):
    return "orders/{0}/attachments/{1}".format(instance.order_id, filename)


class Customer(models.Model):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    contact_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def get_orders_count(self):
        return self.orders.count()

    def get_customer_number(self):
        return str(self.id).zfill(6)

    def __str__(self):
        return "%s" % (self.name)


class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    branch = models.ForeignKey(
        "settings.Branch", on_delete=models.SET_NULL, related_name="orders", null=True, blank=True
    )
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True)
    account = models.ForeignKey(
        "accounts.Account", on_delete=models.SET_NULL, related_name="orders", null=True, blank=True
    )
    promo_code = models.ForeignKey(
        "accounts.Code", on_delete=models.SET_NULL, related_name="order", null=True, blank=True
    )
    total_amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    total_discount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    total_fees = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    order_amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    order_type = models.CharField(
        max_length=30,
        choices=OrderType.choices,
        default=OrderType.DELIVERY,
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethods.choices,
        default=PaymentMethods.BANK_TRANSFER,
    )
    order_notes = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    order_date = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s : %s %s %s" % (
            self.customer,
            self.total_amount,
            self.total_discount,
            self.total_fees,
        )

    def get_order_number(self):
        return str(self.id).zfill(6)

    def get_last_order_status(self):
        try:
            return self.histories.latest("created").order_status
        except:
            return None

    def get_last_order_stage(self):
        try:
            match self.histories.latest("created").order_status:
                case OrderStatus.PENDING:
                    return 1
                case OrderStatus.AWAITING_DELIVERY | OrderStatus.AWAITING_PICKUP:
                    return 2
                case OrderStatus.ON_DELIVERY:
                    return 3
                case OrderStatus.CANCELLED | OrderStatus.COMPLETED | OrderStatus.REFUNDED:
                    return 4
                case _:
                    None
        except:
            return None

    def get_promo_code_account_four_levels(self):
        if self.promo_code:
            return self.promo_code.account.get_four_level_referrers()
        return []

    def get_order_total_point_values(self):
        data = {}
        for detail in self.details.all():
            for value in detail.product_variant.point_values.all():
                data[value.membership_level.level] = {
                    "total": data.get(value.membership_level.level, {}).get("total", 0)
                    + (value.point_value * detail.quantity),
                    "level": value.membership_level.level,
                    "membership_level": value.membership_level.name,
                }

        return data


class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="details",
        null=True,
    )
    product_variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
    )
    quantity = models.IntegerField(
        default=0,
        blank=True,
    )
    amount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    discount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    total_amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    def get_total_point_values(self):
        # data = {}
        data = []
        for value in self.product_variant.point_values.all():
            # data[value.membership_level.level] = {
            #     "total": value.point_value * self.quantity,
            #     "level": value.membership_level.level,
            #     "membership_level": value.membership_level.name,
            # }
            data.append(
                {
                    "total": value.point_value * self.quantity,
                    "level": value.membership_level.level,
                    "membership_level": value.membership_level.name,
                }
            )

        return data

    def __str__(self):
        return "%s : %s %s %s" % (
            self.order,
            self.product_variant,
            self.amount,
            self.discount,
        )


class OrderFee(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="fees",
        null=True,
    )
    fee_type = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s : %s %s" % (
            self.order,
            self.fee_type,
            self.amount,
        )


class OrderAddress(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="address",
        null=True,
    )
    address1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    address2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    zip = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    province = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self):
        return "%s - %s %s %s %s %s %s" % (
            self.order,
            self.address1,
            self.address2,
            self.city,
            self.zip,
            self.province,
            self.country,
        )


class OrderAttachments(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
    )
    attachment = models.ImageField(blank=True, upload_to=order_attachments_directory)

    def __str__(self):
        return "%s" % (self.order)


class OrderHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="histories",
        null=True,
    )
    order_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    notes = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email_sent = models.BooleanField(
        default=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, related_name="created_order_history", null=True, blank=True
    )

    def __str__(self):
        return "%s - %s" % (self.order, self.order_status)

    def get_order_status_stage(self):
        match self.order_status:
            case OrderStatus.PENDING:
                return 1
            case OrderStatus.AWAITING_DELIVERY | OrderStatus.AWAITING_PICKUP:
                return 2
            case OrderStatus.ON_DELIVERY | OrderStatus.ON_PICKUP:
                return 3
            case OrderStatus.CANCELLED | OrderStatus.COMPLETED | OrderStatus.REFUNDED:
                return 4

    def get_order_default_note(self):
        match self.order_status:
            case OrderStatus.PENDING:
                return "Order Status moved to Pending"
            case OrderStatus.AWAITING_DELIVERY:
                return "Order Status moved to Awaiting Delivery"
            case OrderStatus.AWAITING_PICKUP:
                return "Order Status moved to Awaiting Pickup"
            case OrderStatus.ON_DELIVERY:
                return "Order Status moved to On Delivery"
            case OrderStatus.ON_PICKUP:
                return "Order Status moved to On Pickup"
            case OrderStatus.CANCELLED:
                return "Order Status moved to Cancelled"
            case OrderStatus.COMPLETED:
                return "Order Status moved to Completed"
            case OrderStatus.REFUNDED:
                return "Order Status moved to Refunded"


class Delivery(models.Model):
    branch = models.ForeignKey(
        "settings.Branch", on_delete=models.CASCADE, related_name="deliveries", null=True, blank=True
    )
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="deliveries", null=True, blank=True
    )
    estimated_arrival = models.DateField(
        blank=True,
        null=True,
    )
    tracking_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    carrier = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_delivery",
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.branch, self.order)
