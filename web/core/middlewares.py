from django.conf import settings
from django.http import JsonResponse


class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.API_KEY = settings.API_KEY

    def __call__(self, request):
        if request.path.startswith("/api"):
            token = request.headers.get("X-Api-Key")
            if token != self.API_KEY:
                return JsonResponse({"success": False, "message": "Invalid API key"})
        return self.get_response(request)
