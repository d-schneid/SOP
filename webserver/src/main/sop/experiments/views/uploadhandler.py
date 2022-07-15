from django.core.cache import cache
from django.core.files.uploadhandler import FileUploadHandler
from django.http.response import HttpResponse, HttpResponseServerError


class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.

    Copied from:
    http://djangosnippets.org/snippets/678/

    See views.py for upload_progress function...
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(
        self, input_data, META, content_length, boundary, encoding=None
    ):
        self.content_length = content_length
        if "X-Progress-ID" in self.request.GET:
            self.progress_id = self.request.GET["X-Progress-ID"]
        elif "X-Progress-ID" in self.request.META:
            self.progress_id = self.request.META["X-Progress-ID"]
        if self.progress_id:
            self.cache_key = "%s_%s" % (
                self.request.META["REMOTE_ADDR"],
                self.progress_id,
            )
            cache.set(self.cache_key, {"length": self.content_length, "uploaded": 0})

    def new_file(*args, **kwargs) -> None:
        pass

    def receive_data_chunk(self, raw_data, start):
        if self.cache_key:
            data = cache.get(self.cache_key)
            data["uploaded"] += self.chunk_size
            cache.set(self.cache_key, data)
        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.cache_key:
            cache.delete(self.cache_key)


def upload_progress(request):
    """
    A view to report back on upload progress.
    Return JSON object with information about the progress of an upload.

    Copied from:
    http://djangosnippets.org/snippets/678/

    See upload.py for file upload handler.
    """
    progress_id = ""
    if "X-Progress-ID" in request.GET:
        progress_id = request.GET["X-Progress-ID"]
    elif "X-Progress-ID" in request.META:
        progress_id = request.META["X-Progress-ID"]
    if progress_id:
        import simplejson

        cache_key = "%s_%s" % (request.META["REMOTE_ADDR"], progress_id)
        data = cache.get(cache_key)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError(
            "Server Error: You must provide X-Progress-ID header or query param."
        )
