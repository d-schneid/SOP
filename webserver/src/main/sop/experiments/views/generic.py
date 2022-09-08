from typing import TypeVar, Any

from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpResponseRedirect, HttpRequest
from django.http.response import HttpResponseBase
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView

_M = TypeVar("_M", bound=Model)


class PostOnlyDeleteView(DeleteView[_M]):
    """
    A generic delete view that is only accessible via POST requests.
    If it is accessed with a GET request, it will redirect to the url specified in the
    success_url attribute that is defined by the subclass.
    It will delete a model of the model class specified in the model attribute with the
    primary key specified in self.kwargs with key "pk". If no model of that class with
    the given primary key exists, it will also redirect to the success_url.
    """

    def dispatch(
            self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        self.success_url = self.success_url or reverse_lazy("home")
        # We don't want the DeleteView to render something, so any GET request (for
        # example when accessing the delete-url) will redirect back to the success url.
        # Only post requests for deleting a model will get handled by the DeleteView.
        if request.method == "GET":
            return HttpResponseRedirect(self.success_url)

        assert request.method == "POST"
        # Check for correct instance ownership
        if not self.request.user == self.get_object().user:
            raise PermissionDenied()

        model_id = self.kwargs["pk"]
        assert model_id is not None
        # If no model with the given pk exists, we also redirect to the success_url.
        if not self.model.objects.filter(pk=model_id).count():
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


class RestrictedUpdateView(UpdateView):

    def dispatch(self, request, *args, **kwargs):
        # Check if dataset belongs to user
        if not self.request.user == self.get_object().user:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
