from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from rest_framework import status, views
from rest_framework.response import Response
from users.enums import *


class AdminLoginView(views.APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
        print()
        if user is None or not user.is_active:
            return Response(
                {
                    "message": "Username or Password is Incorrect",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if (
            user.user_type != UserType.ADMIN
            and user.user_type != UserType.STAFF
            and user.user_type != UserType.DEVELOPER
        ):
            return Response(
                {"message": "Unauthorized Access"},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)
        return Response(
            data={
                "message": "Login Successful",
            },
            status=status.HTTP_200_OK,
        )


class MemberLoginView(views.APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        user = authenticate(username=request.data.get("username"), password=request.data.get("password"))

        if user is None or not user.is_active:
            return Response(
                {
                    "message": "Username or Password is Incorrect",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(
            data={
                "message": "Login Successful",
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return Response(
            {
                "message": "Logout Successful",
            },
            status=status.HTTP_200_OK,
        )


class WhoAmIMemberView(views.APIView):
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.id:
            return Response(
                data={},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)


class WhoAmIAdminView(views.APIView):
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.id
            and (
                request.user.user_type == UserType.ADMIN
                or request.user.user_type == UserType.STAFF
                or request.user.user_type == UserType.DEVELOPER
            )
        ):
            return Response(
                data={},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)


class WhichUserView(views.APIView):
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.id
            and (
                request.user.user_type == UserType.ADMIN
                or request.user.user_type == UserType.STAFF
                or request.user.user_type == UserType.DEVELOPER
            )
        ):
            return Response(
                data={"user_id": request.user.user_id, "username": request.user.username},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(data={}, status=status.HTTP_401_UNAUTHORIZED)
