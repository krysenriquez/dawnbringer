from typing import Type
from django.http.request import HttpRequest
from rest_framework.permissions import BasePermission
from users.enums import UserType


class IsDeveloperUser(BasePermission):
    def has_permission(self, request: Type[HttpRequest], view):
        return bool(request.user and request.user.user_type.user_type_name == UserType.DEVELOPER)


class IsAdminUser(BasePermission):
    def has_permission(self, request: Type[HttpRequest], view):
        return bool(request.user and request.user.user_type.user_type_name == UserType.ADMINISTRATOR)


class IsStaffUser(BasePermission):
    def has_permission(self, request: Type[HttpRequest], view):
        return bool(request.user and (request.user.user_type.user_type_name == UserType.STAFF or request.user.user_type.user_type_name == UserType.AUDITOR))


class IsMemberUser(BasePermission):
    def has_permission(self, request: Type[HttpRequest], view):
        return bool(request.user and request.user.user_type.user_type_name == UserType.MEMBER)
