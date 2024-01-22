# custom_middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

class BanCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_banned:
            logout(request)  # Log out banned users
            return redirect(reverse('banned_page'))  # Redirect to a ban page

        response = self.get_response(request)
        return response


class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/yougottatryharderthanthathackercmonnow/'):  # Replace with your admin URL
            if not request.user.is_authenticated or not request.user.is_superuser:
                return redirect('/')  # Redirect unauthorized users to another page
        return self.get_response(request)