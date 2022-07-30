from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.forms import Form
from django.http import HttpResponse, HttpRequest

from authentication.forms import LoginForm


class LoginView(DjangoLoginView):
    """
    Custom LoginView.
    """

    form_class = LoginForm

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()

        # Check is form is invalid and set error messages
        if not form.is_valid():
            error_text = ' '.join(
                [error_message for error in form.errors.values() for error_message in error])

            messages.error(request, f"Invalid Login: {error_text}")
        return super().post(request, *args, **kwargs)
    # def form_valid(self, form: Form) -> HttpResponse:


class LogoutView(DjangoLogoutView):
    """
    Custom LogoutView.
    """
