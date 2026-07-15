from django.utils.cache import add_never_cache_headers
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated:
            add_never_cache_headers(response)
        return response

class AdminProtectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        # If the user is trying to access an admindashboard route
        if path.startswith('/admindashboard/'):
            # Allow access to login/logout routes
            allowed_paths = [
                reverse('admin_login'),
                reverse('admin_login_process'),
                reverse('admin_logout_process'),
            ]
            if path not in allowed_paths:
                # If they are not authenticated, redirect them to the home page
                if not request.user.is_authenticated:
                    return redirect('home_page')
