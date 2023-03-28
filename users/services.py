import logging
import json
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from users.models import User
from settings.models import Branch, BranchAssignment
from users.models import UserLogs, Permission, UserType, Module

logger = logging.getLogger(__name__)


def transform_user_form_data_to_json(request):
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


def process_create_user_request(request):
    data = {
        "username": request.data.get("username", None),
        "display_name": request.data.get("display_name", None),
        "email_address": request.data.get("email_address", None),
        "password": request.data.get("password", None),
        "user_type": request.data.get("user_type", None),
        "is_active": request.data.get("is_active", None),
        "created_by": request.user.pk,
        "modified_by": request.user.pk,
    }

    return data


def create_branch_assignment(request):
    assignment = BranchAssignment.objects.create(user=request, created_by=request, modified_by=request)
    if assignment:
        return True
    return False


def create_new_user(request):
    user_type = UserType.objects.get(user_type_name=request.get("user_type_name"))

    data = {
        "username": request.get("username"),
        "email_address": request.get("email_address"),
        "display_name": request.get("display_name"),
        "user_type": user_type,
    }
    user = User.objects.create(**data)
    user.set_password(request["password"])
    user.save()
    return user


def update_branch_assignments(request):
    request_branches = request.data["branch"]
    assignment = BranchAssignment.objects.get(user__user_id=request.data["user_id"])
    added_branches = []

    for branch in request_branches:
        branch_obj = Branch.objects.get(branch_id=branch["branch_id"])
        assignment.branch.add(branch_obj)
        added_branches.append(branch_obj.id)

    for branch in assignment.branch.all():
        if branch.id not in added_branches:
            assignment.branch.remove(branch)


def update_role_permissions(request):
    request_permissions = request.data.get("permissions")
    user_type = UserType.objects.get(user_type_id=request.data.get("user_type_id"))

    for permission in request_permissions:
        print(permission)
        if permission.get("id"):
            try:
                updated_permission = Permission.objects.filter(id=permission.get("id")).update(
                    can_create=permission.get("can_create"),
                    can_retrieve=permission.get("can_retrieve"),
                    can_delete=permission.get("can_delete"),
                    can_update=permission.get("can_update"),
                )
                print(updated_permission)
            except Exception as e:
                print(e)
                raise e
        else:
            try:
                module = Module.objects.get(id=permission.get("module"))
                Permission.objects.create(
                    user_type=user_type,
                    module=module,
                    can_create=permission.get("can_create"),
                    can_retrieve=permission.get("can_retrieve"),
                    can_delete=permission.get("can_delete"),
                    can_update=permission.get("can_update"),
                )
            except Exception as e:
                print(e)
                raise e


def create_user_logs(
    user=None,
    action_type=None,
    content_type_model=None,
    object_id=None,
    object_type=None,
    object_uuid=None,
    value_to_display=None,
):
    content_type = ContentType.objects.get(model=content_type_model)

    log = UserLogs.objects.create(
        user=user,
        action_type=action_type,
        content_type=content_type,
        object_id=object_id,
        object_type=object_type,
        object_uuid=object_uuid,
        value_to_display=value_to_display,
    )

    if log:
        logger.info("Created User Log: " + serializers.serialize("json", [log]))
    else:
        logger.error("Unable to create User Log")
