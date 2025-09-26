import logging

logger = logging.getLogger(__name__)

class LogOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            logger.info(f"HTTP_ORIGIN : {origin}")
        return self.get_response(request)