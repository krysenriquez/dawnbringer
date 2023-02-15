from django.template.loader import render_to_string
from django.template import Template, Context
from rest_framework import status, views
from rest_framework.response import Response
from emails.services import construct_and_send_email_payload, get_email_template, render_template


class Test(views.APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email_template = get_email_template("Registration")
        email_subject = render_template(email_template.subject, {"customer": "Krystjyn Lynnyrd Enriquez"})
        email_body = render_template(
            email_template.body, {"customer": "Krystjyn Lynnyrd Enriquez", "link": "localhost:8000/dbwebapi/register"}
        )
        email_msg = construct_and_send_email_payload(
            "tcisupport@topchoiceinternational.com", email_subject, email_body, "lereussi.developer@gmail.com"
        )
        return Response(
            data={"detail": email_msg},
            status=status.HTTP_200_OK,
        )
