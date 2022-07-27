import json
import random
import string
from unittest.mock import MagicMock

import django.test
from django.core.cache import cache
from django.urls import reverse_lazy

from experiments.views.uploadhandler import UploadProgressCachedHandler, upload_progress


class UploadHandlerTests(django.test.TestCase):
    def test_uploadhandler(self) -> None:
        content = ["Line 1\n", "Line 2\n", "Last Line"]
        uuid = "".join(random.choice(string.digits) for _ in range(32))

        # Request mock for upload handler
        request_mock = MagicMock()
        request_mock.GET = {"X-Progress-ID": str(uuid)}
        request_mock.META["REMOTE_ADDR"] = "127.0.0.1"
        request_mock.META.__getitem__.return_value = "127.0.0.1"

        # Request mock for getting the progress
        get_request = MagicMock()
        get_request.GET = {"X-Progress-ID": str(uuid)}
        get_request.META = {"X-Progress-ID": str(uuid), "REMOTE_ADDR": "127.0.0.1"}
        json_response = json.loads(upload_progress(get_request).content)
        self.assertDictEqual(json_response, {"state": "starting"})

        upload_hanlder = UploadProgressCachedHandler(request=request_mock)

        META = {}  # type: ignore
        content_length = sum([len(bytes(line, "utf-8")) for line in content])
        upload_hanlder.handle_raw_input(None, META, content_length, "")  # type: ignore

        size_received = 0
        for line in content:
            # Send data to upload handler
            data = bytes(line, "utf-8")
            upload_hanlder.chunk_size = len(data)
            upload_hanlder.receive_data_chunk(data, 0)
            size_received += len(data)
            cache_entry = cache.get(upload_hanlder.cache_key)
            self.assertEqual(cache_entry["received"], size_received)
            self.assertEqual(cache_entry["state"], "uploading")

            # check progress with progress view
            response = self.client.get(
                reverse_lazy("upload-progress"), {"X-Progress-ID": str(uuid)}
            )
            json_response = json.loads(response.content)
            self.assertDictEqual(
                json_response,
                {
                    "state": "uploading",
                    "size": content_length,
                    "received": size_received,
                },
            )

        cache_entry = cache.get(upload_hanlder.cache_key)
        self.assertEqual(cache_entry["received"], content_length)
        self.assertEqual(cache_entry["state"], "uploading")

        upload_hanlder.upload_complete()
        cache_entry = cache.get(upload_hanlder.cache_key)
        self.assertEqual(cache_entry["state"], "done")

    def test_uploadhandler_no_request(self) -> None:
        """
        In this test we do not pass a request to the upload handler. It should not activate.
        @return:
        """
        content = ["Line 1\n", "Line 2\n", "Last Line"]
        uuid = "".join(random.choice(string.digits) for _ in range(32))

        # Request mock for getting the progress
        get_request = MagicMock()
        get_request.GET = {"X-Progress-ID": str(uuid)}
        get_request.META = {"X-Progress-ID": str(uuid), "REMOTE_ADDR": "127.0.0.1"}
        json_response = json.loads(upload_progress(get_request).content)
        self.assertDictEqual(json_response, {"state": "starting"})

        upload_hanlder = UploadProgressCachedHandler(request=None)

        META = {}  # type: ignore
        content_length = sum([len(bytes(line, "utf-8")) for line in content])
        upload_hanlder.handle_raw_input(None, META, content_length, "")  # type: ignore

        size_received = 0
        for line in content:
            # Send data to upload handler
            data = bytes(line, "utf-8")
            upload_hanlder.chunk_size = len(data)
            upload_hanlder.receive_data_chunk(data, 0)
            size_received += len(data)
            cache_entry = cache.get(upload_hanlder.cache_key)
            self.assertIsNone(cache_entry)

            # check progress with progress view
            response = self.client.get(
                reverse_lazy("upload-progress"), {"X-Progress-ID": str(uuid)}
            )
            json_response = json.loads(response.content)
            self.assertDictEqual(
                json_response,
                {
                    "state": "starting",
                },
            )

    def test_upload_progress_no_progress_id(self) -> None:
        response = self.client.get(reverse_lazy("upload-progress"))
        self.assertEqual(response.status_code, 500)
