from django.http import JsonResponse
from rest_framework.views import exception_handler, set_rollback
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
    else:
        response = Response(
            {
                'detail': 'Unhandled server error',
                'status_code': 500
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        set_rollback()

    return response


# Django global handlers

def handler404(request, exception):
    return JsonResponse({
        'detail': 'Not found',
        'status_code': 404
    }, status=404)


def handler500(request):
    return JsonResponse({
        'detail': 'Internal server error',
        'status_code': 500
    }, status=500)


def handler403(request, exception):
    return JsonResponse({
        'detail': 'Permission denied',
        'status_code': 403
    }, status=403)


def handler400(request, exception):
    return JsonResponse({
        'detail': 'Bad request',
        'status_code': 400
    }, status=400)