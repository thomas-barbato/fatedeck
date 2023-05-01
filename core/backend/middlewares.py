from django.http import JsonResponse, HttpResponseRedirect


class JsonableResponseMixin:
    def form_invalid(self, form):
        """docstring"""
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        """docstring"""
        if self.request.is_ajax():
            data = {"message": "Successfully submitted form data."}
            return JsonResponse(data)
        return super().form_valid(form)


class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return response