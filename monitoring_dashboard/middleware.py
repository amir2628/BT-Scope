# middleware.py
from django.shortcuts import redirect
from django.urls import reverse

# class AuthenticationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if not request.user.is_authenticated and not request.path == reverse('login'):
#             return redirect('login')
#         response = self.get_response(request)
#         return response


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [reverse('login'), reverse('register'), reverse('landing')]
        if not request.user.is_authenticated and request.path not in allowed_paths:
            return redirect('landing')
        response = self.get_response(request)
        return response
    
# from django.shortcuts import redirect
# from django.urls import reverse

# class OperatorOnlyMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.path.startswith('/cnc') and not request.user.groups.filter(name='Operators').exists():
#             return redirect(reverse('unauthorized'))
#         return self.get_response(request)
