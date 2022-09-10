from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin


class SingleObjectPermissionMixin(SingleObjectMixin):
    """
    A mixin for testing for access permissions to a specific instance of a model.
    Current implementation checks if user owns the model instance.
    """

    def dispatch(self, request, *args, **kwargs):
        # Check if model belongs to user
        if not request.user == self.get_object().user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
