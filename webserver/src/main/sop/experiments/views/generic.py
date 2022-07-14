from django.http import HttpResponseRedirect, HttpRequest
from django.http.response import HttpResponseBase
from django.views.generic import DeleteView


class PostOnlyDeleteView(DeleteView):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        # We don't want the DeleteView to render something, so any GET request (for
        # example when accessing the delete-url) will redirect back to the success url.
        # Only post requests for deleting a model will get handled by the DeleteView.
        if request.method == "GET":
            return HttpResponseRedirect(self.success_url)

        assert request.method == "POST"
        model_id = self.kwargs["pk"]
        assert model_id is not None
        # If no model with the given pk exists, we also redirect to the success_url.
        if not self.model.objects.filter(pk=model_id).count():
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)
