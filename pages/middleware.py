from django.http import HttpResponsePermanentRedirect

class CaseInsensitiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if path.lower() != path:
            new_path = path.lower()
            if request.GET:
                query_string = request.META.get('QUERY_STRING', '')
                print(query_string)
                new_path = f'{new_path}?{query_string}'
            return HttpResponsePermanentRedirect(new_path)
        response = self.get_response(request)
        return response