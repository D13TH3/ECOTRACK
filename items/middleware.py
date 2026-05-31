from django.shortcuts import redirect
from django.conf import settings

class LastStateMiddleware:
    """Middleware to remember whether the user last left the app logged-in or logged-out.

    - When an authenticated user makes requests, set a persistent cookie `last_state=dashboard`.
    - When the logout handler sets `request.session['just_logged_out']`, this middleware writes
      `last_state=items` to the response and clears the session flag.
    - On visits to the root or login page, redirect users based on the `last_state` cookie:
      * authenticated -> `/items/dashboard/`
      * not authenticated and last_state==items -> `/items/`
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Redirect early for root or login pages based on cookie/state
        path = request.path
        login_paths = [getattr(settings, 'LOGIN_URL', '/accounts/login/'), '/', '/accounts/login/']
        last_state = request.COOKIES.get('last_state')

        if path in login_paths:
            if request.user.is_authenticated:
                return redirect('dashboard')
            if (not request.user.is_authenticated) and last_state == 'items':
                return redirect('item_list')

        response = self.get_response(request)

        try:
            if request.session.pop('just_logged_out', False):
                response.set_cookie('last_state', 'items', max_age=30 * 24 * 3600)
            elif request.user.is_authenticated:
                response.set_cookie('last_state', 'dashboard', max_age=30 * 24 * 3600)
        except Exception:
            pass

        return response
