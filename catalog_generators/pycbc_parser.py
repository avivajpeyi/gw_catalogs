# -*- coding: utf-8 -*-
"""Module one liner

This module does what....

Example usage:

"""

import glob
import os

import h5py
import pandas as pd
from bilby.gw.conversion import (
    component_masses_to_chirp_mass,
    luminosity_distance_to_redshift
)
from tqdm import tqdm

from .event_keys import gwosc_keys
from .utils import dict_to_json, summarise_samples

DATA_DIR = "../data/pycbc_search/"

SEARCH_PARAMS = {
    "mass1": "The source-frame mass of the larger object, in solar masses",
    "mass2": "The source-frame mass of the smaller object, in solar masses",
    "chi_eff": "The effective spin of the binary",
    "chi_p": "The precessing-spin parameter of the binary",
    "spin1_a": "The dimensionless spin-magnitude of the larger object",
    "spin2_a": "The dimensionless spin-magnitude of the smaller object",
    "spin1_azimuthal": "The azimuthal angle of the spin of the larger object",
    "spin2_azimuthal": "The azimuthal angle of the spin of the smaller object",
    "spin1_polar": "The polar angle of the spin of the spin of the larger object",
    "spin2_polar": "The polar angle of the spin of the spin of the smaller object",
    "tc": "The geocentric GPS time of the signal merger",
    "ra": "The right ascension of the signal (in radians)",
    "dec": "The declination of the signal (in radians)",
    "distance": "The lumionsity distance to the signal (in Mpc)",
    "redshift": "The cosmological redshift of the signal",
    "comoving_volume": "The comoving volume at the redshift of the signal",
    "inclination": "The inclination of the binary's orbital angular momentum with respect to the line of sight, in radians. An inclination of 0 (pi) corresponds to a face-on (face-away) orientation",
    "polarization": "The polarization angle of the gravitational wave",
    "loglikelihood": "The natural log of the likelihood of each sample",
    "logprior": "The natural log of the prior of each sample",
    "logjacobian": "The natural log of the Jacobian between the parameter space and the sampling parameter-space that was used",
}


def main():
    generate_pycbc_catalog(data_dir=DATA_DIR,
                           out_catalog_fname="../data/pycbc_catalog.json")


def generate_pycbc_catalog(data_dir, out_catalog_fname):
    event_samples = load_event_samples_to_dataframes(data_dir)
    event_samples = make_events_gwosc_compatible(event_samples)
    event_summary = summarise_all_events(event_samples)
    dict_to_json(
        json_fname=out_catalog_fname,
        data_dict=dict(events=event_summary)
    )
    print("Completed catalog generation.")


def summarise_all_events(events_samples_dict):
    summary_dict = {}
    for event_name, event_df in events_samples_dict.items():
        event_summary_dict = summarise_event_df(event_df)
        event_summary_dict['commonName'] = event_name
        summary_dict[event_name] = event_summary_dict
    return summary_dict


def load_event_samples_to_dataframes(data_dir):
    """Load PyCBC hdf files into dict of df"""
    events_samples_dict = {}
    files = glob.glob(os.path.join(data_dir, "*.hdf"))
    for file in tqdm(files, desc="Reading PyCBC Posteriors", total=len(files)):
        event_name = os.path.basename(file).replace(".hdf", "")
        event_name = event_name.replace("H1L1V1-EXTRACT_POSTERIOR_", "GW")
        event_hdf = h5py.File(file, mode='r')
        event_dict = {k: event_hdf[f"samples/{k}"][()] for k in SEARCH_PARAMS.keys()}
        event_df = pd.DataFrame(event_dict)
        events_samples_dict[event_name] = event_df
    return events_samples_dict


def make_events_gwosc_compatible(events_df_container):
    for event_name in events_df_container.keys():
        events_df_container[event_name] = convert_df_to_gwosc_df(
            events_df_container[event_name])
    return events_df_container


def convert_df_to_gwosc_df(df: pd.DataFrame) -> pd.DataFrame:
    converted_df = df.copy()
    # rename
    converted_df['GPS'] = converted_df['tc']
    converted_df['mass_1'] = converted_df['mass1']
    converted_df['mass_2'] = converted_df['mass2']
    converted_df['total_mass'] = converted_df['mass_1'] + converted_df['mass_2']
    converted_df['luminosity_distance'] = converted_df['distance']

    # re-parameterisation
    converted_df['chirp_mass'] = component_masses_to_chirp_mass(
        mass_1=converted_df['mass_1'],
        mass_2=converted_df['mass_2']
    )

    for key in ['mass_1', 'mass_2', 'chirp_mass', 'total_mass']:
        converted_df[f'{key}_source'] = \
            converted_df[key] / (1 + converted_df[f'redshift'])

    return converted_df


def summarise_event_df(event_df):
    summary = {}
    for param in event_df.columns:
        summary[f"{param}_lower"], summary[f"{param}_upper"], summary[param] = \
            summarise_samples(event_df[param])

    for param_type in ["_lower", "_upper", ""]:
        summary[f'redshift{param_type}'] = \
            float(luminosity_distance_to_redshift(
                summary[f'luminosity_distance{param_type}']))

    summary = {k: summary.get(k, None) for k in gwosc_keys}
    summary['version'] = 1
    summary['reference'] = "https://github.com/gwastro/2-ogc"
    summary['catalog.shortName'] = "PyCBC"
    return summary


if __name__ == "__main__":
    main()
