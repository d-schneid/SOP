import json
from typing import Any, Dict, IO, Optional

from django.core.cache import cache
from django.core.files.uploadhandler import FileUploadHandler
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseServerError


class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request: Optional[HttpRequest] = None) -> None:
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id: Optional[str] = None
        self.cache_key: Optional[str] = None

    def handle_raw_input(
        self,
        input_data: IO[bytes],
        META: Dict[str, str],
        content_length: int,
        boundary: str,
        encoding: Optional[str] = None,
    ) -> None:
        if self.request is None:
            return

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
            cache.set(
                self.cache_key,
                {"size": self.content_length, "received": 0, "state": "uploading"},
            )

    def new_file(*args: Any, **kwargs: Any) -> None:
        pass

    def receive_data_chunk(self, raw_data: bytes, start: int) -> bytes:
        if self.cache_key:
            data = cache.get(self.cache_key)
            data["received"] += self.chunk_size
            cache.set(self.cache_key, data)
        return raw_data

    def file_complete(self, file_size: int) -> None:
        pass

    def upload_complete(self) -> None:
        if self.cache_key:
            data = cache.get(self.cache_key)
            data["state"] = "done"
            cache.set(self.cache_key, data)


def upload_progress(request: HttpRequest) -> HttpResponse:
    """
    A view to report back on upload progress.
    Return JSON object with information about the progress of an upload.
    The JSON object matches the specifications of the nginx-upload-progress module.
    """
    progress_id = ""
    if "X-Progress-ID" in request.GET:
        progress_id = request.GET["X-Progress-ID"]
    elif "X-Progress-ID" in request.META:
        progress_id = request.META["X-Progress-ID"]
    if progress_id:
        cache_key = "%s_%s" % (request.META["REMOTE_ADDR"], progress_id)
        data = cache.get(cache_key)
        data = data or {"state": "starting"}
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseServerError(
            "Server Error: You must provide X-Progress-ID header or query param."
        )
