from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin


class LoginRequiredMixin(DjangoLoginRequiredMixin):
    """
    Custom LoginRequiredMixin.
    """

    login_url = "/login/"
