import glob
import os

import numpy as np
import pandas as pd
from bilby.gw.conversion import (
    chirp_mass_and_mass_ratio_to_total_mass,
    luminosity_distance_to_redshift,
    total_mass_and_mass_ratio_to_component_masses
)
from tqdm import tqdm

from .event_keys import gwosc_keys
from .utils import dict_to_json, summarise_samples

DATA_DIR = "../data/ias_search/"

# Parameters from IAS Github repo https://github.com/jroulet/O2_samples/
SEARCH_PARAMS = {
    "mchirp": "chirp mass",
    "eta": "mass ratio",
    "s1z": "aligned spin of primary",
    "s2z": "aligned spin of secondary",
    "RA": "right ascension",
    "DEC": "declination",
    "psi": "polarization angle",
    "iota": "inclination",
    "vphi": "orbital phase",
    "tc": "arrival time, with arbitrary offset",
    "DL": "luminosity distance",
}

GPS_TIME = {
    'GW151216': 1134293073.164,
    'GW170121': 1169069154.565,
    'GW170202': 1170079035.715,
    'GW170304': 1172680691.356,
    'GW170425': 1177134832.178,
    'GW170727': 1185152688.019,
    'GW170403': 1175295989.221,
    'GW150914': 1126259462.411,
    'GW151226': 1135136350.585,
    'GW170104': 1167559936.582,
    'GW170608': 1180922494.5,
    'GW170729': 1185389807.311,
    'GW170809': 1186302519.740,
    'GW170814': 1186741861.519,
    'GW170818': 1187058327.075,
    'GW170823': 1187529256.500,
    'GW151012': 1128678900.428,
    'GW170817A': 186974184.716,
}


def main():
    generate_ias_catalog(data_dir=DATA_DIR,
                         out_catalog_fname="../data/ias_catalog.json")


def generate_ias_catalog(data_dir, out_catalog_fname):
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
        event_summary_dict['GPS'] = GPS_TIME[event_name]
        summary_dict[event_name] = event_summary_dict
    return summary_dict


def load_event_samples_to_dataframes(data_dir):
    """Load IAS npy files into dict of df"""
    events_samples_dict = {}
    files = glob.glob(os.path.join(data_dir, "*.npy"))
    for file in tqdm(files, desc="Reading IAS Posteriors", total=len(files)):
        event_name = os.path.basename(file).replace(".npy", "")
        event_df = pd.DataFrame(dict(zip(
            list(SEARCH_PARAMS.keys()),
            np.load(file).T
        )))
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
    converted_df['chirp_mass'] = converted_df['mchirp']
    converted_df['mass_ratio'] = converted_df['eta']
    converted_df['luminosity_distance'] = converted_df['DL']
    # re-parameterisation
    converted_df['total_mass'] = \
        chirp_mass_and_mass_ratio_to_total_mass(
            converted_df['chirp_mass'],
            converted_df['mass_ratio']
        )
    converted_df['mass_1'], converted_df['mass_2'] = \
        total_mass_and_mass_ratio_to_component_masses(
            converted_df['mass_ratio'],
            converted_df['total_mass']
        )
    converted_df['chi_eff'] = (converted_df['s1z'] +
                               converted_df['s2z'] *
                               converted_df['mass_ratio']) / \
                              (1 + converted_df['mass_ratio'])

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
        for key in ['mass_1', 'mass_2', 'chirp_mass', 'total_mass']:
            summary[f'{key}_source{param_type}'] = \
                summary[f"{key}{param_type}"] / (1 + summary[f'redshift{param_type}'])

    summary = {k: summary.get(k, None) for k in gwosc_keys}
    summary['version'] = 1
    summary['reference'] = "https://github.com/jroulet/O2_samples/"
    summary['catalog.shortName'] = "IAS"
    return summary


if __name__ == "__main__":
    main()
