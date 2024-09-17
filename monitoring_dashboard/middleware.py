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


from django.http import HttpResponseForbidden

class BlockDirectAccessMiddleware:
    """
    Middleware to block direct access to certain URLs from both authenticated and anonymous users,
    while still allowing requests with specific headers or referrer (e.g., JavaScript or trusted sources).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.restricted_urls = [
            '/get-operators/',
            '/add-material/',
            '/add-schedule/',
            '/get-schedule/',
            '/get-schedule-details/',
            '/delete-schedule/',
            '/delete-schedule-table/<int:id>/',
            '/update-schedule/',
            '/add-finished-product/',
            '/add-delivered-product/',
            '/get-materials-chart-data/',
            '/get-inventory-chart-data/',
            '/get-deliveries-chart-data/',
            '/get_production_schedule_data/',
            '/submit_form/<str:schedule>/',
            '/delete_schedule_entries/',
            '/create_schedule/',
            '/get_production_schedule_row/',
            '/update_production_schedule_data/',
            '/delete_schedule_entries/',
            '/update_cnc_status/',
            '/start-work/',
            '/finish-work/',
            '/end-shift/',
            '/resume-work/',
            '/get-schedule-details-Timer-elapsed/<int:schedule_id>/',
            '/api/employees/',
            

            '/instruments/data/',
        ]

    def __call__(self, request):
        # Check if the request is for one of the restricted URLs
        if request.path in self.restricted_urls:
            # Block if the request doesn't meet the criteria (e.g., no valid custom header or referrer)
            if not self._is_allowed_request(request):
                return HttpResponseForbidden("Страница не найдена...")

        response = self.get_response(request)
        return response

    def _is_allowed_request(self, request):
        """
        Define the criteria for allowing access, such as checking for a custom header or referrer.
        Modify this method based on your security requirements.
        """
        # Check if the request contains a valid custom header (sent from trusted JS or frontend)
        # You can customize this logic to allow requests only from specific sources
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':  # Example: Allow AJAX requests only
            return True

        # Optionally, allow requests from specific referrers
        # allowed_referrers = ['http://yourfrontenddomain.com/your-page/']
        allowed_referrers = [
            'http://localhost:8000/',   # Allow all pages from localhost:8000
            'http://127.0.0.1:8000/'    # Allow all pages from 127.0.0.1:8000
        ]

        if request.META.get('HTTP_REFERER') in allowed_referrers:
            return True

        # Block all other requests
        return False
