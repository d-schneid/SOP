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
class PyodAlgorithm:
    file_name: str
    class_name: str
    display_name: str
    group: Algorithm.AlgorithmGroup


PYOD_ALGORITHMS = [
    PyodAlgorithm("abod.py", "ABOD", "ABOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm(
        "anogan.py", "AnoGAN", "AnoGAN", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm(
        "auto_encoder.py",
        "AutoEncoder",
        "AutoEncoder",
        Algorithm.AlgorithmGroup.NEURAL_NETWORKS,
    ),
    # This is NOT consistent with the current state of the file. We need to cover this
    # special case in the code to rename the class of the algorithm (that's currently
    # called AutoEncoder) to AutoEncoderTorch, so it does not collide with the normal
    # AutoEncoder algorithm
    PyodAlgorithm(
        "auto_encoder_torch.py",
        "AutoEncoderTorch",
        "AutoEncoder (torch)",
        Algorithm.AlgorithmGroup.NEURAL_NETWORKS,
    ),
    PyodAlgorithm(
        "cblof.py", "CBLOF", "CBLOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED
    ),
    PyodAlgorithm("cd.py", "CD", "CD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("cof.py", "COF", "COF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("copod.py", "COPOD", "COPOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm(
        "deep_svdd.py", "DeepSVDD", "DeepSVDD", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm("ecod.py", "ECOD", "ECOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm(
        "feature_bagging.py",
        "FeatureBagging",
        "FeatureBagging",
        Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES,
    ),
    PyodAlgorithm("gmm.py", "GMM", "GMM", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("hbos.py", "HBOS", "HBOS", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm(
        "iforest.py", "IForest", "IForest", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    PyodAlgorithm(
        "inne.py", "INNE", "INNE", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    PyodAlgorithm("kde.py", "KDE", "KDE", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("knn.py", "KNN", "KNN", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("lmdd.py", "LMDD", "LMDD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("loci.py", "LOCI", "LOCI", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm(
        "loda.py", "LODA", "LODA", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    PyodAlgorithm("lof.py", "LOF", "LOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm(
        "lscp.py", "LSCP", "LSCP", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    PyodAlgorithm("mad.py", "MAD", "MAD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("mcd.py", "MCD", "MCD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm(
        "mo_gaal.py", "MO_GAAL", "MO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm("ocsvm.py", "OCSVM", "OCSVM", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("pca.py", "PCA", "PCA", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("rod.py", "ROD", "ROD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm(
        "sampling.py", "Sampling", "Sampling", Algorithm.AlgorithmGroup.PROBABILISTIC
    ),
    PyodAlgorithm(
        "so_gaal.py", "SO_GAAL", "SO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm("sod.py", "SOD", "SOD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("sos.py", "SOS", "SOS", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm(
        "suod.py", "SUOD", "SUOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
    PyodAlgorithm("vae.py", "VAE", "VAE", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm(
        "xgbod.py", "XGBOD", "XGBOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES
    ),
]


def rename_algorithm_file_if_needed(
    pyod_algo: PyodAlgorithm, pyod_models_root: Path
) -> None:
    file_name, ext = os.path.splitext(pyod_algo.file_name)
    if file_name != pyod_algo.class_name.lower():
        new_file_name = pyod_algo.class_name.lower()
        os.rename(
            pyod_models_root / (file_name + ext),
            pyod_models_root / (new_file_name + ext),
        )
        pyod_algo.file_name = new_file_name + ext


def replace_occurrences(
    pyod_algo: PyodAlgorithm, pyod_models_root: Path, old: str, new: str
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


MISSING = object()


class Command(BaseCommand):
    help = "Adds all pyod algorithms as algorithm models into to database"
    quiet = False

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--quiet", "-q", action="store_true", help="Turn off console output."
        )

    def check_algorithm_validity(
        self, pyod_algo: PyodAlgorithm, pyod_models_root: Path
    ):
        # Check algorithms before adding them to the database
        self.stdout_write(
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

        self.stdout_write(self.style.SUCCESS("OK"))

    def save_algorithms_in_db(self, pyod_algo: PyodAlgorithm, pyod_models_root: Path):
        self.stdout_write(
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
            self.stdout_write(self.style.SUCCESS("OK"))
        else:
            self.stdout_write(self.style.NOTICE("ALREADY EXISTS"))

    def stdout_write(self, message: str, ending: str = MISSING):
        if self.quiet:
            return

        if ending is not MISSING:
            self.stdout.write(message, ending=ending)
        else:
            self.stdout.write(message)

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        import pyod

        self.quiet = options["quiet"]

        self.stdout_write(
            "Searching for pyod library path...",
            ending="",
        )

        pyod_path = Path(pyod.__path__[0])
        self.stdout_write(self.style.SUCCESS("FOUND"))

        media_pyod_root = settings.ALGORITHM_ROOT_DIR / "pyod_algorithms"
        pyod_models_dir = media_pyod_root / "models"

        if os.path.exists(media_pyod_root):
            self.stdout_write(
                "Pyod algorithms already exist in media root, deleting...", ending=""
            )
            shutil.rmtree(media_pyod_root)
            self.stdout_write(self.style.SUCCESS("OK"))

        self.stdout_write("Copying pyod library to media root...", ending="")
        shutil.copytree(src=pyod_path, dst=media_pyod_root)
        self.stdout_write(self.style.SUCCESS("OK"))

        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))

        # Fix the BaseDetector imports to import absolute from pyod and not relative.
        # This is needed since the check for validity by the AlgorithmLoader checks for
        # inheritance of pyod.models.BaseDetector, which does not equal
        # .base.BaseDetector
        self.stdout_write(
            "Change import statements for pyod.models.base.BaseDetector...", ending=""
        )
        for algo in PYOD_ALGORITHMS:
            replace_occurrences(
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
                replace_occurrences(
                    algo, pyod_models_dir, "AutoEncoder", "AutoEncoderTorch"
                )
        self.stdout_write(self.style.SUCCESS("OK"))

        # Rename algorithm files if they don't fulfill the requirement of matching
        # file name and class name
        self.stdout_write("Rename python files to match class names...", ending="")
        for algo in PYOD_ALGORITHMS:
            rename_algorithm_file_if_needed(algo, pyod_models_dir)
        self.stdout_write(self.style.SUCCESS("OK"))

        # Check algorithms for validity with the AlgorithmLoader
        self.stdout_write("Perform validity checks for algorithms:")
        for algo in PYOD_ALGORITHMS:
            self.check_algorithm_validity(algo, pyod_models_dir)

        # Finally save the algorithms in the database
        self.stdout_write("Saving models to database:")
        for algo in PYOD_ALGORITHMS:
            self.save_algorithms_in_db(algo, pyod_models_dir)
        return None
