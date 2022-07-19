from __future__ import annotations

from typing import List

from django.http import HttpRequest

from experiments.models import Experiment, Algorithm


def string_cleanup(s: str, strict=True) -> str:
    s = s.strip()
    if s.startswith('"') and s.endswith('"') or s.startswith("'") and s.endswith("'"):
        return s[1:-1]

    # If strict is not set, we allow strings that are not wrapped in quotes.
    if not strict:
        return s

    raise TypeError(f"{s} is not of type string")


def convert_string_to_matching_type(s: str) -> str | int | float | List[object] | None:
    # None variation
    if s is None or s.strip() == "None":
        return None
    s = s.strip()
    # int
    if s.isdigit():
        return int(s)
    # float (one dot and without dot it's a digit, kinda hacky)
    if s.replace(".", "", 1).isdigit():
        return float(s)
    # List of items
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
        return [convert_string_to_matching_type(sub) for sub in s.split(",")]
    # Dictionary
    # TODO: maybe implement dictionary parsing
    if s.startswith("{") and s.endswith("}"):
        raise NotImplementedError("Parsing dictionaries is not supported")
    # Everything else has to be a string
    return string_cleanup(s)


def get_params_out_of_form(
    request: HttpRequest, experiment: Experiment
) -> dict[str, dict[str, object]]:
    dikt = {}
    for algo in experiment.algorithms.all():
        algo: Algorithm
        algo_dict = {}
        for param_name, param_default in algo.get_signature_as_json().items():
            form_key = f"{algo.pk}_{param_name}"
            form_value = request.POST[form_key]

            # The type of the given value is not the expected type
            if not isinstance(form_value, type(param_default)):
                # The type of the default value is None, so we do our best in parsing the value ourselves
                if param_default is None or type(param_default) is None:
                    form_value = convert_string_to_matching_type(
                        str(form_value)
                    )  # type: ignore

                # type is known, so we parse the value accordingly
                else:
                    form_value = type(param_default)(form_value)

            # The type is str and str was expected. Do some string cleanup to remove potential quotes
            elif type(param_default) == str:
                form_value = string_cleanup(str(form_value))

            # Add this param to the algorithms specific dictionary
            algo_dict.update({str(param_name): form_value})

        # Add the algorithms specific dictionary to the global dictionary and go on to the next algorithm
        dikt.update({str(algo.pk): algo_dict})
    return dikt
