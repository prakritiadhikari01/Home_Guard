# app/interfaces/api/exception_handlers.py
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        detail = response.data.get("detail")
        code = getattr(detail, "code", None)  # ErrorDetail carries .code even though str() drops it
        if code:
            response.data["code"] = code

    return response