from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginForm

class SOPLoginView(LoginView):
    """
    Custom LoginView.
    """

    form_class = LoginForm

class SOPLogoutView(LogoutView):
    """
    Custom LogoutView.
    """

    pass