import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import django.test
from django.conf import settings

from experiments.services.algorithm import (
    save_temp_algorithm,
    delete_temp_algorithm,
    convert_param_mapping_to_signature_dict,
)


class AlgorithmServicesTests(django.test.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    def setUp(self) -> None:
        self.init_mocks()
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        super().setUp()

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDown()

    def init_mocks(self) -> None:
        self.user = MagicMock()
        self.user.id = 1
        self.content = ["Line 1\n", "Line 2\n", "Last Line"]
        self.file = MagicMock()
        self.file.name = "test_file.txt"
        self.file.chunks.return_value = [bytes(line, "utf-8") for line in self.content]

    def assert_temp_file_created(self, temp_path: Path) -> None:
        self.assertEqual(
            temp_path,
            settings.MEDIA_ROOT
            / "algorithms"
            / "temp"
            / f"{self.user.id}"
            / self.file.name,
        )
        self.assertTrue(os.path.exists(temp_path))
        with open(temp_path, "r") as f:
            for index, line in enumerate(f):
                self.assertEqual(line, self.content[index])

    def test_save_temp_algorithm_valid(self) -> None:
        temp_path = save_temp_algorithm(self.user, self.file)
        self.assert_temp_file_created(temp_path)
        os.remove(temp_path)

    def test_save_temp_algorithm_empty_file(self) -> None:
        self.content = []
        self.init_mocks()
        temp_path = save_temp_algorithm(self.user, self.file)
        self.assert_temp_file_created(temp_path)
        os.remove(temp_path)

    def test_delete_temp_algorithm(self) -> None:
        path = settings.MEDIA_ROOT / "algorithms" / "temp" / "3" / "temp.txt"
        os.makedirs(path.parent)
        with open(path, "w") as f:
            f.write("Text")
        delete_temp_algorithm(path)
        self.assertFalse(os.path.exists(path))
        self.assertFalse(os.path.exists(path.parent))

    def test_delete_temp_algorithm_wrong_dir(self) -> None:
        path = settings.MEDIA_ROOT / "temp.txt"
        with open(path, "w") as f:
            f.write("Text")
        assert os.path.exists(path)
        self.assertRaises(AssertionError, delete_temp_algorithm, path)
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_delete_temp_algorithm_keep_dir_when_not_empty(self) -> None:
        path = settings.MEDIA_ROOT / "algorithms" / "temp" / "3" / "temp.txt"
        path2 = settings.MEDIA_ROOT / "algorithms" / "temp" / "3" / "temp2.txt"
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "w") as f:
            f.write("Text")
        with open(path2, "w") as f:
            f.write("Text")
        assert os.path.exists(path)
        assert os.path.exists(path2)

        delete_temp_algorithm(path)
        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists(path2))

    def test_convert_param_mapping_to_signature_dict(self) -> None:
        param1 = MagicMock()
        param1.default = 5
        param2 = MagicMock()
        param2.default = "Text"
        param3 = MagicMock()
        param3.default = ["Hello", "World"]
        param4 = MagicMock()
        param4.default = 3.14
        param5 = MagicMock()
        param5.default = None
        param6 = MagicMock()
        param6.default = str
        params = {
            "param1": param1,
            "param2": param2,
            "param3": param3,
            "param4": param4,
            "param5": param5,
            "param6": param6,
            "args": "Not in dict",
            "kwargs": "Algo not in dict",
        }
        dikt = convert_param_mapping_to_signature_dict(params)  # type: ignore
        self.assertDictEqual(
            dikt,
            {
                "param1": param1.default,
                "param2": param2.default,
                "param3": param3.default,
                "param4": param4.default,
                "param5": param5.default,
                "param6": None,
            },
        )

    def test_convert_param_mapping_to_signature_dict_empy_mapping(self) -> None:
        dikt = convert_param_mapping_to_signature_dict(dict())  # type: ignore
        self.assertDictEqual(dikt, dict())
