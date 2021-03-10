import abc
from typing import Dict, List

import pandas as pd
from bilby.gw.conversion import luminosity_distance_to_redshift

from . import utils
from .event_keys import GWOSC_KEYS


class EventParser:

    def __init__(self, datasource, catalog, samples):
        self.name = utils.get_event_name(datasource)
        self.datasource = datasource
        self.catalog = catalog
        self.samples = self.standardise_samples(samples)

    @staticmethod
    @abc.abstractmethod
    def get_search_parameters()->List[str]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def load_event_samples(cls, sample_filename: str):
        raise NotImplementedError

    @staticmethod
    @utils.sort_parameters
    @abc.abstractmethod
    def standardise_samples(samples: pd.DataFrame) -> pd.DataFrame:
        return samples

    def summarise_event(self) -> Dict:
        summary = {}
        for param in self.samples.columns:
            summary[f"{param}_lower"], summary[f"{param}_upper"], summary[param] = \
                utils.summarise_samples(self.samples[param])

        for param_type in ["_lower", "_upper", ""]:
            summary[f'redshift{param_type}'] = \
                float(luminosity_distance_to_redshift(
                    summary[f'luminosity_distance{param_type}']))
            for key in ['mass_1', 'mass_2', 'chirp_mass', 'total_mass']:
                summary[f'{key}_source{param_type}'] = \
                    summary[f"{key}{param_type}"] / (
                            1 + summary[f'redshift{param_type}'])

        summary = {k: summary.get(k, None) for k in GWOSC_KEYS}
        summary['reference'] = self.datasource
        summary['catalog.shortName'] = self.catalog
        summary['commonName'] = self.name
        return summary
