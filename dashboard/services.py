import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth, TruncDate, TruncYear, Coalesce
from django.db.models import Q, Max, Min, F, Count, Sum, When, Case, DecimalField, IntegerField
from accounts.models import Account
from orders.enums import OrderStatus
from orders.models import Order, Customer


def get_obj_count(obj, period, param, filter):
    data = []
    match period:
        case "Day":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__date")
            for x in reversed(range(7)):
                date_filter = today - relativedelta(days=x)
                filters[property_filter] = date_filter
                total = obj.aggregate(
                    total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                data.append({"period": date_filter, "total": total})
            return data
        case "Month":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__month")
            for x in reversed(range(6)):
                date_filter = today - relativedelta(months=x)
                filters[property_filter] = date_filter.month
                total = obj.aggregate(
                    total=Coalesce(
                        Count(param, filter=Q(**filters)),
                        0,
                        output_field=IntegerField(),
                    )
                ).get("total")
                data.append(
                    {"period": "-".join((str(date_filter.year), "{:02d}".format(date_filter.month))), "total": total}
                )
            return data
        case "Year":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__year")
            for x in reversed(range(3)):
                date_filter = today - relativedelta(years=x)
                filters[property_filter] = date_filter.year
                total = obj.aggregate(
                    total=Coalesce(
                        Count(param, filter=Q(**filters)),
                        0,
                        output_field=IntegerField(),
                    )
                ).get("total")
                data.append({"period": str(date_filter.year), "total": total})
            return data
        case _:
            return []


def get_obj_total(obj, period, param, filter):
    data = []
    match period:
        case "Day":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__date")
            for x in reversed(range(7)):
                date_filter = today - relativedelta(days=x)
                filters[property_filter] = date_filter
                total = obj.aggregate(
                    total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=DecimalField())
                ).get("total")
                data.append({"period": date_filter, "total": total})
            return data
        case "Month":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__month")
            for x in reversed(range(6)):
                date_filter = today - relativedelta(months=x)
                filters[property_filter] = date_filter.month
                total = obj.aggregate(
                    total=Coalesce(
                        Sum(param, filter=Q(**filters)),
                        0,
                        output_field=DecimalField(),
                    )
                ).get("total")
                data.append(
                    {"period": "-".join((str(date_filter.year), "{:02d}".format(date_filter.month))), "total": total}
                )
            return data
        case "Year":
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__year")
            for x in reversed(range(3)):
                date_filter = today - relativedelta(years=x)
                filters[property_filter] = date_filter.year
                total = obj.aggregate(
                    total=Coalesce(
                        Sum(param, filter=Q(**filters)),
                        0,
                        output_field=DecimalField(),
                    )
                ).get("total")
                data.append({"period": str(date_filter.year), "total": total})
            return data
        case _:
            return []


def get_obj_count_group_by(object, period, grouping, param, filter):
    data = []
    for obj in object:
        match period:
            case "Day":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__date")
                total = 0
                for x in reversed(range(7)):
                    date_filter = today - relativedelta(days=x)
                    filters[property_filter] = date_filter
                    filters[grouping] = getattr(obj, grouping)
                    count = object.aggregate(
                        total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                    ).get("total")
                    total += count

                data.append({"name": getattr(obj, grouping), "total": total})
            case "Month":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__month")
                total = 0
                for x in reversed(range(6)):
                    date_filter = today - relativedelta(months=x)
                    filters[property_filter] = date_filter.month
                    filters[grouping] = getattr(obj, grouping)
                    count = object.aggregate(
                        total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                    ).get("total")
                    total += count

                data.append({"name": getattr(obj, grouping), "total": total})
            case "Year":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__year")
                total = 0
                for x in reversed(range(6)):
                    date_filter = today - relativedelta(years=x)
                    filters[property_filter] = date_filter.year
                    filters[grouping] = getattr(obj, grouping)
                    count = object.aggregate(
                        total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                    ).get("total")
                    total += count

                data.append({"name": getattr(obj, grouping), "total": total})
            case _:
                return []
    else:
        return data


def get_obj_total_group_by(object, period, grouping, param, filter):
    data = []
    for obj in object:
        match period:
            case "Day":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__date")
                total = 0
                for x in reversed(range(7)):
                    date_filter = today - relativedelta(days=x)
                    filters[property_filter] = date_filter
                    filters[grouping] = getattr(obj, grouping)
                    sum = object.aggregate(
                        total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=DecimalField())
                    ).get("total")
                    total += sum

                data.append({"name": getattr(obj, grouping), "total": total})
            case "Month":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__month")
                total = 0
                for x in reversed(range(6)):
                    date_filter = today - relativedelta(months=x)
                    filters[property_filter] = date_filter.month
                    filters[grouping] = getattr(obj, grouping)
                    sum = object.aggregate(
                        total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=DecimalField())
                    ).get("total")
                    total += sum

                data.append({"name": getattr(obj, grouping), "total": total})
            case "Year":
                today = datetime.date.today()
                filters = {}
                property_filter = "%s%s" % (filter, "__year")
                total = 0
                for x in reversed(range(6)):
                    date_filter = today - relativedelta(years=x)
                    filters[property_filter] = date_filter.year
                    filters[grouping] = getattr(obj, grouping)
                    sum = object.aggregate(
                        total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=DecimalField())
                    ).get("total")
                    total += sum

                data.append({"name": getattr(obj, grouping), "total": total})
            case _:
                return []
    else:
        return data


def get_obj_aggregate_count(object, period, param, filter, description):
    match period:
        case "Day":
            period_length = 7
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__date")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(days=x)
                filters[property_filter] = date_filter
                count = object.aggregate(
                    total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += count
            return {"total": total, "description": "%s for the past %s days" % (description, period_length)}
        case "Month":
            period_length = 6
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__month")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(months=x)
                filters[property_filter] = date_filter.month
                count = object.aggregate(
                    total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += count
            return {"total": total, "description": "%s for the past %s months" % (description, period_length)}
        case "Year":
            period_length = 6
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__year")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(years=x)
                filters[property_filter] = date_filter.year
                count = object.aggregate(
                    total=Coalesce(Count(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += count
            return {"total": total, "description": "%s for the past %s years" % (description, period_length)}
        case _:
            return {}


def get_obj_aggregate_total(object, period, param, filter, label, description):
    match period:
        case "Day":
            period_length = 7
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__date")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(days=x)
                filters[property_filter] = date_filter
                sum = object.aggregate(
                    total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += sum
            return {
                "total": total,
                "description": "%s for the past %s days" % (description, period_length),
                "label": label,
            }
        case "Month":
            period_length = 6
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__month")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(months=x)
                filters[property_filter] = date_filter.month
                sum = object.aggregate(
                    total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += sum
            return {
                "total": total,
                "description": "%s for the past %s months" % (description, period_length),
                "label": label,
            }
        case "Year":
            period_length = 6
            today = datetime.date.today()
            filters = {}
            property_filter = "%s%s" % (filter, "__year")
            total = 0
            for x in reversed(range(period_length)):
                date_filter = today - relativedelta(years=x)
                filters[property_filter] = date_filter.year
                sum = object.aggregate(
                    total=Coalesce(Sum(param, filter=Q(**filters)), 0, output_field=IntegerField())
                ).get("total")
                total += sum

            return {
                "total": total,
                "description": "%s for the past %s years" % (description, period_length),
                "label": label,
            }
        case _:
            return {}
