from django.db import models
from orders.enums import AddressType
from orders.enums import AddressType, OrderType, PaymentMethods, OrderStatus

# Orders
def order_attachments_directory(instance, filename):
    return "orders/{0}/attachments/{1}".format(instance.id, filename)


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

    def __str__(self):
        return "%s" % (self.name)


class Address(models.Model):
    customer = models.ForeignKey(
        Customer,
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
    address_type = models.CharField(
        max_length=11,
        choices=AddressType.choices,
        default=AddressType.BILLING,
    )

    def __str__(self):
        return "%s : %s %s %s %s - %s" % (
            self.customer,
            self.address1,
            self.address2,
            self.city,
            self.province,
            self.address_type,
        )


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True)
    account = models.ForeignKey(
        "accounts.Account", on_delete=models.SET_NULL, related_name="account_order", null=True, blank=True
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
    total_amount = models.DecimalField(
        default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True
    )
    discount = models.DecimalField(default=0, max_length=256, decimal_places=2, max_digits=13, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

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


class OrderAttachments(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
    )
    attachment = models.ImageField(blank=True, upload_to=order_attachments_directory)


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
            case OrderStatus.ON_DELIVERY:
                return 3
            case OrderStatus.CANCELLED | OrderStatus.COMPLETED | OrderStatus.REFUNDED:
                return 4
