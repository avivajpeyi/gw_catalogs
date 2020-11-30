from typing import List, Optional

import corner
import numpy as np
import json


def summarise_samples(
        samples: np.ndarray,
        quantiles: Optional[List[float]] = [0.16, 0.84]
):
    """Converts df to lower upper median valus
    :return: lower, upper, median
    """
    qtles = corner.quantile(x=samples, q=quantiles)
    return (
        qtles[0],
        qtles[1],
        np.median(samples)
    )


def dict_to_json(json_fname, data_dict):
    with open(json_fname, 'w') as fp:
        json.dump(data_dict, fp, indent=2, sort_keys=True)
