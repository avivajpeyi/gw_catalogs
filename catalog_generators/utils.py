import json
import re
from typing import List, Optional

import corner
import numpy as np
from astropy import units
from astropy.cosmology import Planck15
from scipy.interpolate import interp1d

from . import event_keys


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


def sort_parameters(samples_standardising_func):
    '''Decorator that sort param and ensure we have the necessary params.'''

    def wrap(*args, **kwargs):
        samples = samples_standardising_func(*args, **kwargs)
        missing_params = event_keys.REQUIRED_PARAMETERS - set(samples.columns.values)
        if len(missing_params)>1:
            raise ValueError(f"The samples are missing values for {missing_params}")
        return samples[event_keys.REQUIRED_PARAMETERS]

    return wrap


def get_event_name(fname):
    return re.findall(r"(\w*\d{6}[a-z]*)", fname)


def get_redshift_from_dl(dl):
    z_array = np.expm1(np.linspace(np.log(1), np.log(11), 1000))
    distance_array = Planck15.luminosity_distance(z_array).to(units.Mpc).value
    z_of_d = interp1d(distance_array, z_array)
    return z_of_d(dl)

def add_aligned_component_spins(df):
    df['spin_1x'], df['spin_1y'], df['spin_1z'] = 0, 0, 1
    df['spin_2x'], df['spin_2y'], df['spin_2z'] = 0, 0, 1
    return df