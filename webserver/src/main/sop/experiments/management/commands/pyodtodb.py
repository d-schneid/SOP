import dataclasses
import os
import shutil
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from backend.task.execution.AlgorithmLoader import AlgorithmLoader
from experiments.models import Algorithm
from experiments.services.algorithm import convert_param_mapping_to_signature_dict


@dataclasses.dataclass
class PyodAlgorithm:
    file_name: str
    class_name: str
    group: Algorithm.AlgorithmGroup


PYOD_ALGORITHMS = [
    PyodAlgorithm("abod.py", "ABOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("anogan.py", "AnoGAN", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm(
        "auto_encoder.py", "AutoEncoder", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm(
        "auto_encoder_torch.py", "AutoEncoder", Algorithm.AlgorithmGroup.NEURAL_NETWORKS
    ),
    PyodAlgorithm("cblof.py", "CBLOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("cd.py", "CD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("cof.py", "COF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("copod.py", "COPOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("deep_svdd.py", "DeepSVDD", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm("ecod.py", "ECOD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm(
        "feature_bagging.py",
        "FeatureBagging",
        Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES,
    ),
    PyodAlgorithm("gmm.py", "GMM", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("hbos.py", "HBOS", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("iforest.py", "IForest", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
    PyodAlgorithm("inne.py", "INNE", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
    PyodAlgorithm("kde.py", "KDE", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("knn.py", "KNN", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("lmdd.py", "LMDD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("loci.py", "LOCI", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("loda.py", "LODA", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
    PyodAlgorithm("lof.py", "LOF", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("lscp.py", "LSCP", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
    PyodAlgorithm("mad.py", "MAD", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("mcd.py", "MCD", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("mo_gaal.py", "MO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm("ocsvm.py", "OCSVM", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("pca.py", "PCA", Algorithm.AlgorithmGroup.LINEAR_MODEL),
    PyodAlgorithm("rod.py", "ROD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("sampling.py", "Sampling", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("so_gaal.py", "SO_GAAL", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm("sod.py", "SOD", Algorithm.AlgorithmGroup.PROXIMITY_BASED),
    PyodAlgorithm("sos.py", "SOS", Algorithm.AlgorithmGroup.PROBABILISTIC),
    PyodAlgorithm("suod.py", "SUOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
    PyodAlgorithm("vae.py", "VAE", Algorithm.AlgorithmGroup.NEURAL_NETWORKS),
    PyodAlgorithm("xgbod.py", "XGBOD", Algorithm.AlgorithmGroup.OUTLIER_ENSEMBLES),
]


def rename_algorithm_files_if_needed(pyod_models_root: Path) -> None:
    for pyod_algo in PYOD_ALGORITHMS:
        file_name, ext = os.path.splitext(pyod_algo.file_name)
        if file_name != pyod_algo.class_name.lower():
            new_file_name = pyod_algo.class_name.lower()
            os.rename(
                pyod_models_root / (file_name + ext),
                pyod_models_root / (new_file_name + ext),
            )
            pyod_algo.file_name = new_file_name + ext


def fix_base_detector_imports(pyod_models_root: Path):
    for pyod_algo in PYOD_ALGORITHMS:
        assert os.path.splitext(pyod_algo.file_name)[0] == pyod_algo.class_name.lower()

    for pyod_algo in PYOD_ALGORITHMS:
        path = pyod_models_root / pyod_algo.file_name
        fh, abs_path = mkstemp()
        with os.fdopen(fh, "w") as new_file:
            with open(path) as old_file:
                for line in old_file:
                    new_file.write(
                        line.replace(
                            "from .base import BaseDetector",
                            "from pyod.models.base import BaseDetector",
                        )
                    )
        # Copy the file permissions from the old file to the new file
        shutil.copymode(path, abs_path)
        # Remove original file
        os.remove(path)
        # Move new file
        shutil.move(abs_path, path)


def save_algorithms_in_db(pyod_models_root: Path):
    # Check algorithms before adding them to the database
    for pyod_algo in PYOD_ALGORITHMS:
        # assert filename matches classname
        assert os.path.splitext(pyod_algo.file_name)[0] == pyod_algo.class_name.lower()
        # check algorithm for validity
        errors = AlgorithmLoader.is_algorithm_valid(
            str(pyod_models_root / pyod_algo.file_name)
        )
        assert errors is None, errors

    for pyod_algo in PYOD_ALGORITHMS:
        path = pyod_models_root / (pyod_algo.class_name.lower() + ".py")
        mapping = AlgorithmLoader.get_algorithm_parameters(str(path))
        params_dict = convert_param_mapping_to_signature_dict(mapping)
        data = {
            "display_name": f"[PYOD] {pyod_algo.class_name}",
            "group": pyod_algo.group,
            "signature": params_dict,
            "user": None,
        }
        algo = Algorithm.objects.create(**data)
        algo.path.name = str(path.relative_to(settings.ALGORITHM_ROOT_DIR))
        algo.save()


class Command(BaseCommand):
    help = "Adds all pyod algorithms as algorithm models into to database"

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        import pyod

        pyod_path = Path(pyod.__path__[0])
        media_pyod_root = settings.ALGORITHM_ROOT_DIR / "pyod_algorithms"
        if os.path.exists(media_pyod_root):
            raise CommandError(
                f"pyod seems to be imported before. {media_pyod_root} exists."
            )

        shutil.copytree(src=pyod_path, dst=media_pyod_root)

        AlgorithmLoader.set_algorithm_root_dir(str(settings.ALGORITHM_ROOT_DIR))

        rename_algorithm_files_if_needed(media_pyod_root / "models")
        fix_base_detector_imports(media_pyod_root / "models")
        save_algorithms_in_db(media_pyod_root / "models")
        return None
