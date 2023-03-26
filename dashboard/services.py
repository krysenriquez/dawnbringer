from django.db.models.functions import TruncMonth, TruncDate, TruncYear, ExtractMonth, ExtractDay, ExtractYear
from django.db.models import (
    Q,
    Max,
    Min,
    F,
    Count,
    Sum,
    FilteredRelation,
)
from orders.enums import OrderStatus
from orders.models import Order, OrderHistory, Customer


def get_order_count(branch_id, period, param):
    match period:
        case "Day":
            return (
                Order.objects.annotate(
                    latest_order_status=FilteredRelation(
                        "histories", condition=Q(histories__created=Max("histories__created"))
                    )
                )
                .values("latest_order_status")
                .annotate(period=TruncDate("created"))
                .values("period", "latest_order_status")
                .annotate(total=Count(param))
                .values("period", "total", "latest_order_status")
                .order_by("-period")
            )
        case "Month":
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(period=TruncMonth("created"))
                .values("period")
                .annotate(total=Count(param))
                .values("period", "total")
                .order_by("-period")
            )
        case "Year":
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(period=TruncYear("created"))
                .values("period")
                .annotate(total=Count(param))
                .values("period", "total")
                .order_by("-period")
            )
        case _:
            return []


def get_order_total(branch_id, period, param):
    match period:
        case "Day":
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(latest_supply_status=Max("histories__created"))
                .filter(
                    Q(histories__created=F("latest_supply_status")) & Q(histories__order_status=OrderStatus.COMPLETED)
                )
                .annotate(period=TruncDate("created"))
                .values("period")
                .annotate(total=Sum(param))
                .values("period", "total")
                .order_by("-period")
            )
        case "Month":
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(latest_supply_status=Max("histories__created"))
                .filter(
                    Q(histories__created=F("latest_supply_status")) & Q(histories__order_status=OrderStatus.COMPLETED)
                )
                .annotate(period=TruncMonth("created"))
                .values("period")
                .annotate(total=Sum(param))
                .values("period", "total")
                .order_by("-period")
            )
        case "Year":
            return (
                Order.objects.filter(branch__branch_id=branch_id)
                .annotate(latest_supply_status=Max("histories__created"))
                .filter(
                    Q(histories__created=F("latest_supply_status")) & Q(histories__order_status=OrderStatus.COMPLETED)
                )
                .annotate(period=TruncYear("created"))
                .values("period")
                .annotate(total=Sum(param))
                .values("period", "total")
                .order_by("-period")
            )
        case _:
            return []


def get_code_usage_count(branch_id, period, param):
    match period:
        case "Day":
            return (
                Order.objects.filter(branch__branch_id=branch_id, promo_code__isnull=False)
                .annotate(period=TruncDate("created"))
                .values("period")
                .annotate(total=Count(param))
                .values("period", "total")
                .order_by("-period")
            )
        case "Month":
            return (
                Order.objects.filter(branch__branch_id=branch_id, promo_code__isnull=False)
                .annotate(period=TruncMonth("created"))
                .values("period")
                .annotate(total=Count(param))
                .values("period", "total")
                .order_by("-period")
            )
        case "Year":
            return (
                Order.objects.filter(branch__branch_id=branch_id, promo_code__isnull=False)
                .annotate(period=TruncYear("created"))
                .values("period")
                .annotate(total=Count(param))
                .values("period", "total")
                .order_by("-period")
            )
        case _:
            return []


def get_customers_count(period, param):
    match period:
        case "Day":
            return (
                Customer.objects.annotate(period=TruncDate("created"))
                .values("period")
                .annotate(count=Count("id"))
                .values("period", "count")
                .order_by("-period")
            )
        case "Month":
            return (
                Customer.objects.annotate(period=TruncMonth("created"))
                .values("period")
                .annotate(count=Count("id"))
                .values("period", "count")
                .order_by("-period")
            )
        case "Year":
            return (
                Customer.objects.annotate(period=TruncYear("created"))
                .values("period")
                .annotate(count=Count("id"))
                .values("period", "count")
                .order_by("-period")
            )
        case _:
            return []
