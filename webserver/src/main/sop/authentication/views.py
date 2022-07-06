from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from authentication.forms import LoginForm


class LoginView(DjangoLoginView):
    """
    Custom LoginView.
    """

    form_class = LoginForm


class LogoutView(DjangoLogoutView):
    """
    Custom LogoutView.
    """
