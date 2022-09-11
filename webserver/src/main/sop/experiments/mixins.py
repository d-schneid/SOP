from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic.detail import SingleObjectMixin


class SingleObjectPermissionMixin(SingleObjectMixin):
    """
    A mixin for testing for access permissions to a specific instance of a model.
    Current implementation checks if user owns the model instance.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Check if model belongs to user
        if not request.user == self.get_object().user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
