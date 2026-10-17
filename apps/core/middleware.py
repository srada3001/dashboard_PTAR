class PrivateCacheMiddleware:
    """Pages are per person: nothing may be kept by a shared cache. Behind Firebase Hosting, its
    CDN would store and serve to others any response marked public (docs/REQUISITOS.md §11).
    Static files are answered earlier by WhiteNoise and keep their own headers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "Cache-Control" not in response:
            response["Cache-Control"] = "private, no-cache"
        return response


class HtmxRedirectMiddleware:
    """A redirect answering an htmx request (expired session, forced password change) would be
    followed by the browser and the login page swapped into a fragment. Turn it into an
    HX-Redirect so htmx loads the target as a full page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.headers.get("HX-Request") == "true" and response.status_code in (301, 302, 303, 307, 308):
            location = response["Location"]
            response.status_code = 204
            del response["Location"]
            response["HX-Redirect"] = location
        return response
