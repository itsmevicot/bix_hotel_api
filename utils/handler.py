import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

from utils.exceptions import ExceptionMessageBuilder

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "error": response.data.get("detail", "An error occurred.")
        }

        extra_details = {k: v for k, v in response.data.items() if k != "detail"}
        if extra_details:
            custom_response["detail"] = extra_details

        logger.error(f"Handled exception: {exc}, Context: {context}")
        return Response(custom_response, status=response.status_code)

    if isinstance(exc, ExceptionMessageBuilder):
        custom_response = {
            "error": exc.message,
            "detail": exc.detail
        }
        logger.error(f"Custom exception: {exc.message} - Details: {exc.detail}")
        return Response(custom_response, status=exc.status_code)

    logger.error("Unhandled exception occurred", exc_info=exc)

    if settings.DEBUG:
        return Response(
            {
                "error": str(exc),
            },
            status=500,
        )

    return Response(
        {
            "error": "An unexpected error occurred.",
        },
        status=500,
    )
