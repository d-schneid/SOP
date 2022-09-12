import copy
import dataclasses
import os
import shutil
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.models import Algorithm
from experiments.services.algorithm import convert_param_mapping_to_signature_dict


@dataclasses.dataclass
class _PyodAlgorithm:
    file_name: str
    class_name: str
    display_name: str
    group: Algorithm.AlgorithmGroup.values


_PYOD_ALGORITHMS = [
    _PyodAlgorithm("abod.py", "ABOD", "ABOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm(
        "anogan.py", "AnoGAN", "AnoGAN", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    _PyodAlgorithm(
        "auto_encoder.py",
        "AutoEncoder",
        "AutoEncoder",
        Algorithm.AlgorithmGroup.NEURAL_NETWORKS,
    ),
    # This is NOT consistent with the current state of the file. We need to cover this
    # special case in the code to rename the class of the algorithm (that's currently
    # called AutoEncoder) to AutoEncoderTorch, so it does not collide with the normal
    # AutoEncoder algorithm
    _PyodAlgorithm(
        "auto_encoder_torch.py",
        "AutoEncoderTorch",
        "AutoEncoder (torch)",
        Algorithm.AlgorithmGroup.NEURAL_NETWORKS,
    ),
    _PyodAlgorithm(
        "cblof.py", "CBLOF", "CBLOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED
    ),
    _PyodAlgorithm("cd.py", "CD", "CD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    _PyodAlgorithm("cof.py", "COF", "COF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm(
        "copod.py", "COPOD", "COPOD", Algorithm.AlgorithmGroup.PROBABILISTIC
    ),
    _PyodAlgorithm(
        "deep_svdd.py", "DeepSVDD", "DeepSVDD", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    _PyodAlgorithm("ecod.py", "ECOD", "ECOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm(
        "feature_bagging.py",
        "FeatureBagging",
        "FeatureBagging",
        Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES,
    ),
    _PyodAlgorithm("gmm.py", "GMM", "GMM", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm("hbos.py", "HBOS", "HBOS", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm(
        "iforest.py", "IForest", "IForest", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    _PyodAlgorithm(
        "inne.py", "INNE", "INNE", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    _PyodAlgorithm("kde.py", "KDE", "KDE", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm("knn.py", "KNN", "KNN", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm("lmdd.py", "LMDD", "LMDD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    _PyodAlgorithm("loci.py", "LOCI", "LOCI", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm(
        "loda.py", "LODA", "LODA", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    _PyodAlgorithm("lof.py", "LOF", "LOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm(
        "lscp.py", "LSCP", "LSCP", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    _PyodAlgorithm("mad.py", "MAD", "MAD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm("mcd.py", "MCD", "MCD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    _PyodAlgorithm(
        "mo_gaal.py", "MO_GAAL", "MO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    _PyodAlgorithm("ocsvm.py", "OCSVM", "OCSVM", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    _PyodAlgorithm("pca.py", "PCA", "PCA", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    _PyodAlgorithm(
        "rgraph.py", "RGraph", "RGraph", Algorithm.AlgorithmGroup.GRAPH_BASED
    ),
    _PyodAlgorithm("rod.py", "ROD", "ROD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm(
        "sampling.py", "Sampling", "Sampling", Algorithm.AlgorithmGroup.PROBABILISTIC
    ),
    _PyodAlgorithm(
        "so_gaal.py", "SO_GAAL", "SO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    _PyodAlgorithm("sod.py", "SOD", "SOD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    _PyodAlgorithm("sos.py", "SOS", "SOS", Algorithm.AlgorithmGroup.PROBABILISTIC),
    _PyodAlgorithm(
        "suod.py", "SUOD", "SUOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    _PyodAlgorithm("vae.py", "VAE", "VAE", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    _PyodAlgorithm(
        "xgbod.py", "XGBOD", "XGBOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
]


def _rename_algorithm_file_if_needed(
    pyod_algo: _PyodAlgorithm, pyod_models_root: Path
) -> None:
    file_name, ext = os.path.splitext(pyod_algo.file_name)
    if file_name != pyod_algo.class_name.lower():
        new_file_name = pyod_algo.class_name.lower()
        os.rename(
            pyod_models_root / (file_name + ext),
            pyod_models_root / (new_file_name + ext),
        )
        pyod_algo.file_name = new_file_name + ext


def _replace_occurrences(
    pyod_algo: _PyodAlgorithm, pyod_models_root: Path, old: str, new: str
):
    path = pyod_models_root / pyod_algo.file_name
    fh, abs_path = mkstemp()

    # Replace occurrences in old file
    with os.fdopen(fh, "w") as new_file:
        with open(path) as old_file:
            for line in old_file:
                new_file.write(line.replace(old, new))

    # Copy the file permissions from the old file to the new file
    shutil.copymode(path, abs_path)
    # Remove original file
    os.remove(path)
    # Move new file
    shutil.move(abs_path, path)


class Command(BaseCommand):
    help = "Adds all pyod algorithms as algorithm models into to database"
    quiet = False

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--quiet", "-q", action="store_true", help="Turn off console output."
        )

    def _check_algorithm_validity(
        self, pyod_algo: _PyodAlgorithm, pyod_models_root: Path
    ):
        # Check algorithms before adding them to the database
        self._stdout_write(
            f"  Checking {pyod_algo.display_name} ({pyod_algo.file_name})"
            " for validity...",
            ending="",
        )
        # assert filename matches classname
        assert os.path.splitext(pyod_algo.file_name)[0] == pyod_algo.class_name.lower()

        # check algorithm for validity
        errors = AlgorithmLoader.is_algorithm_valid(
            str(pyod_models_root / pyod_algo.file_name)
        )
        assert errors is None, errors

        self._stdout_write(self.style.SUCCESS("OK"))

    def _save_algorithms_in_db(self, pyod_algo: _PyodAlgorithm, pyod_models_root: Path):
        self._stdout_write(
            f"  Saving {pyod_algo.display_name} ({pyod_algo.file_name})"
            " into database...",
            ending="",
        )
        path = pyod_models_root / (pyod_algo.class_name.lower() + ".py")
        mapping = AlgorithmLoader.get_algorithm_parameters(str(path))
        params_dict = convert_param_mapping_to_signature_dict(mapping)
        data = {
            "display_name": f"[PYOD] {pyod_algo.display_name}",
            "group": pyod_algo.group,
            "signature": params_dict,
            "user": None,
        }
        algo, created = Algorithm.objects.get_or_create(**data)
        if created:
            algo.path.name = str(path.relative_to(settings.MEDIA_ROOT))
            algo.save()
            self._stdout_write(self.style.SUCCESS("OK"))
        else:
            self._stdout_write(self.style.NOTICE("ALREADY EXISTS"))

    def _stdout_write(self, message: str, ending: Optional[str] = None):
        if self.quiet:
            return

        if ending is None:
            self.stdout.write(message)
        else:
            self.stdout.write(message, ending=ending)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        global _PYOD_ALGORITHMS
        # save the original state of the PYOD_ALGORITHMS list
        original_pyod_algorithms = copy.deepcopy(_PYOD_ALGORITHMS)

        result = self._execute(*args, **options)

        # reset the original attribute
        _PYOD_ALGORITHMS = original_pyod_algorithms

        return result

    def _execute(self, *args: Any, **options: Any) -> Optional[str]:
        import pyod

        self.quiet = options["quiet"]

        self._stdout_write(
            "Searching for pyod library path...",
            ending="",
        )

        pyod_path = Path(list(pyod.__path__)[0])
        self._stdout_write(self.style.SUCCESS("FOUND"))

        media_pyod_root = settings.ALGORITHM_ROOT_DIR / "pyod_algorithms"
        pyod_models_dir = media_pyod_root / "models"

        if os.path.exists(media_pyod_root):
            self._stdout_write(
                "Pyod algorithms already exist in media root, deleting...", ending=""
            )
            shutil.rmtree(media_pyod_root)
            self._stdout_write(self.style.SUCCESS("OK"))

        self._stdout_write("Copying pyod library to media root...", ending="")
        shutil.copytree(src=pyod_path, dst=media_pyod_root)
        self._stdout_write(self.style.SUCCESS("OK"))

        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))

        # Fix the BaseDetector imports to import absolute from pyod and not relative.
        # This is needed since the check for validity by the AlgorithmLoader checks for
        # inheritance of pyod.models.BaseDetector, which does not equal
        # .base.BaseDetector
        self._stdout_write(
            "Change import statements for pyod.models.base.BaseDetector...", ending=""
        )
        for algo in _PYOD_ALGORITHMS:
            _replace_occurrences(
                algo,
                pyod_models_dir,
                "from .base import BaseDetector",
                "from pyod.models.base import BaseDetector",
            )
            # AutoEncoderTorch is a special case, since the class name of it is the same
            # as the class of the normal AutoEncoder. This results in both algorithms
            # having the same file name and therefore using the same code.
            # We replace every occurrence of AutoEncoder with AutoEncoderTorch, so it
            # doesn't collide with the normal AutoEncoder and we can continue normally
            if algo.file_name == "auto_encoder_torch.py":
                _replace_occurrences(
                    algo, pyod_models_dir, "AutoEncoder", "AutoEncoderTorch"
                )
        self._stdout_write(self.style.SUCCESS("OK"))

        # Rename algorithm files if they don't fulfill the requirement of matching
        # file name and class name
        self._stdout_write("Rename python files to match class names...", ending="")
        for algo in _PYOD_ALGORITHMS:
            _rename_algorithm_file_if_needed(algo, pyod_models_dir)
        self._stdout_write(self.style.SUCCESS("OK"))

        # Check algorithms for validity with the AlgorithmLoader
        self._stdout_write("Perform validity checks for algorithms:")
        for algo in _PYOD_ALGORITHMS:
            self._check_algorithm_validity(algo, pyod_models_dir)

        # Finally save the algorithms in the database
        self._stdout_write("Saving models to database:")
        for algo in _PYOD_ALGORITHMS:
            self._save_algorithms_in_db(algo, pyod_models_dir)
        return None
