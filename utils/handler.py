from rest_framework.response import Response
from rest_framework.views import exception_handler

from utils.exceptions import ExceptionMessageBuilder


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'status': 'error',
            'message': response.data.get('detail', 'An error occurred.'),
        }

        if len(response.data) > 1:
            custom_response['detail'] = {k: v for k, v in response.data.items() if k != 'detail'}
        return Response(custom_response, status=response.status_code)

    if isinstance(exc, ExceptionMessageBuilder):
        custom_response = {
            'status': 'error',
            'message': exc.message,
            'detail': exc.detail
        }
        return Response(custom_response, status=exc.status_code)

    return Response({
        'status': 'error',
        'message': 'An unexpected error occurred.',
    }, status=500)
