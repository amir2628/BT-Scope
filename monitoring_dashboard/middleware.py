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
            # '/get_production_schedule_data/',
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
            '/api/save_shift/',
            '/api/shifts/<int:year>/<int:month>/',
            '/instruments/data/',
            '/instruments/save/',
            '/instruments/delete/<int:instrument_id>/',
            '/threadrings/data/',
            
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





# this is for capturing user activity logs:

from django.utils.timezone import now
from monitoring_dashboard.models import UserActivityLog

# class UserActivityLoggerMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Log the request body and query parameters (POST or GET data)
#         request_data = request.POST if request.method == 'POST' else request.GET

#         # Call the view and get the response
#         response = self.get_response(request)

#         if request.user.is_authenticated:
#             print(f"Logging activity for user: {request.user.username}")
#             # Log to the database
#             UserActivityLog.objects.create(
#                 user=request.user,
#                 username=request.user.username,
#                 first_name=request.user.first_name,
#                 middle_name=request.user.middle_name,
#                 last_name=request.user.last_name,
#                 role=request.user.role,
#                 position=request.user.position,
#                 email=request.user.email,
#                 path=request.path,
#                 method=request.method,
#                 timestamp=now(),
#                 ip_address=request.META.get('REMOTE_ADDR'),
#                 request_data=dict(request_data),  # Convert QueryDict to regular dict
#                 response_data=response.content.decode('utf-8')[:500]  # Capture first 500 characters of the response (adjust as needed)
#             )

#         return response

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class UserActivityLoggerMiddleware:
    EXCLUDED_PATHS = [
        '/get-machine-status/',
        '/activity-logs/',
        '/activity-logs/data/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip logging for excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)

        # Log the request body and query parameters (POST or GET data)
        request_data = request.POST if request.method == 'POST' else request.GET

        # Call the view and get the response
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Log to the database
            UserActivityLog.objects.create(
                user=request.user,
                username=request.user.username,
                first_name=request.user.first_name,
                middle_name=request.user.middle_name,
                last_name=request.user.last_name,
                role=request.user.role,
                position=request.user.position,
                email=request.user.email,
                path=request.path,
                method=request.method,
                timestamp=now(),
                # ip_address=request.META.get('REMOTE_ADDR'),
                ip_address=get_client_ip(request),  # Use updated function to fetch IP
                request_data=dict(request_data),  # Convert QueryDict to regular dict
                response_data=response.content.decode('utf-8')[:500]  # Capture first 500 characters of the response (adjust as needed)
            )

        return response
